from __future__ import annotations

import asyncio
import logging
from datetime import timedelta
from pathlib import Path
from typing import Awaitable, Callable
from uuid import uuid4

from aiohttp import web  # type: ignore[import-untyped]

from consumer.application.ports.configuration_provider_port import (
    ConfigurationProviderPort,
)
from consumer.application.ports.game_session_provider import GameSessionProvider
from consumer.application.scheduler.scheduler import Scheduler
from consumer.application.scheduler.tasks.autosave_task import AutosaveTask
from consumer.application.scheduler.tasks.health_check_task import HealthCheckTask
from consumer.application.scheduler.tasks.metrics_task import MetricsTask
from consumer.application.scheduler.tasks.resolve_vote_task import ResolveVoteTask
from consumer.application.scheduler.tasks.tick_task import TickTask
from consumer.application.use_cases.administration_use_cases import (
    ChangeControlModeUseCase,
    ReloadConfigurationUseCase,
)
from consumer.application.use_cases.gameplay_use_cases import (
    ResolveInputUseCase,
    SubmitInputUseCase,
    TickEmulatorUseCase,
)
from consumer.application.use_cases.monitoring_use_cases import (
    CollectMetricsUseCase,
    GetStatusUseCase,
    HealthCheckUseCase,
)
from consumer.application.use_cases.player_use_cases import (
    ConnectPlayerUseCase,
    DisconnectPlayerUseCase,
)
from consumer.application.use_cases.save_use_cases import (
    AutosaveUseCase,
    ManualSaveUseCase,
)
from consumer.application.use_cases.session_use_cases import (
    PauseSessionUseCase,
    RestoreSessionUseCase,
    ResumeSessionUseCase,
    StartSessionUseCase,
    StopSessionUseCase,
)
from consumer.application.use_cases.voting_use_cases import ResolveVoteUseCase
from consumer.domain.entities.game_session import GameSession
from consumer.domain.enums import ControlMode
from consumer.domain.value_objects import SessionConfiguration, SessionId
from consumer.infrastructure.configuration.file_configuration_provider import (
    FileConfigurationProvider,
)
from consumer.infrastructure.emulator.pyboy_adapter import PyBoyAdapter
from consumer.infrastructure.monitoring.logger_adapter import LoggerAdapter
from consumer.infrastructure.monitoring.metrics_publisher import MetricsPublisher
from consumer.infrastructure.persistence.file_save_repository import (
    FileSaveRepository,
)
from consumer.infrastructure.persistence.singleton_game_session_provider import (
    SingletonGameSessionProvider,
)
from consumer.infrastructure.streaming.aiortc_video_publisher import (
    AiortcVideoPublisher,
)
from consumer.presentation.api import register_routes
from consumer.presentation.middleware import setup_middleware

_LOG = logging.getLogger(__name__)

_FRAME_INTERVAL = timedelta(seconds=1 / 60)
_METRICS_INTERVAL = timedelta(seconds=60)
_HEALTH_CHECK_INTERVAL = timedelta(seconds=30)

_DEFAULT_CONFIG = SessionConfiguration(
    control_mode=ControlMode.FIFO,
    voting_interval=timedelta(seconds=30),
    autosave_interval=timedelta(seconds=15),
)


async def _load_config(config_path: Path) -> SessionConfiguration:
    provider: ConfigurationProviderPort = FileConfigurationProvider(config_path)
    try:
        return await provider.load()
    except FileNotFoundError:
        return _DEFAULT_CONFIG


async def _restore_save(repository: FileSaveRepository, pyboy: PyBoyAdapter) -> None:
    try:
        data = await repository.load()
        await pyboy.restore_snapshot(data)
    except FileNotFoundError:
        pass


def create_app(
    config_path: Path,
    rom_path: Path,
    save_dir: Path,
) -> web.Application:
    _setup_logging()
    logger = LoggerAdapter(_LOG)

    session_config = asyncio.get_event_loop().run_until_complete(
        _load_config(config_path)
    )

    pyboy = PyBoyAdapter(rom_path)
    save_repository = FileSaveRepository(save_dir)
    config_provider = FileConfigurationProvider(config_path)

    publisher = AiortcVideoPublisher(pyboy)

    asyncio.get_event_loop().run_until_complete(_restore_save(save_repository, pyboy))

    session = GameSession(session_id=SessionId(uuid4()), configuration=session_config)
    session_provider: GameSessionProvider = SingletonGameSessionProvider(session)

    metrics_publisher = MetricsPublisher(logger)

    use_cases: dict[str, object] = {
        "start_session": StartSessionUseCase(session_provider),
        "stop_session": StopSessionUseCase(session_provider),
        "pause_session": PauseSessionUseCase(session_provider),
        "resume_session": ResumeSessionUseCase(session_provider),
        "restore_session": RestoreSessionUseCase(
            session_provider, pyboy, save_repository
        ),
        "connect_player": ConnectPlayerUseCase(session_provider),
        "disconnect_player": DisconnectPlayerUseCase(session_provider),
        "submit_input": SubmitInputUseCase(session_provider),
        "resolve_input": ResolveInputUseCase(session_provider, pyboy),
        "tick_emulator": TickEmulatorUseCase(session_provider, pyboy, publisher),
        "change_control_mode": ChangeControlModeUseCase(session_provider),
        "reload_configuration": ReloadConfigurationUseCase(
            session_provider, config_provider
        ),
        "collect_metrics": CollectMetricsUseCase(session_provider, metrics_publisher),
        "health_check": HealthCheckUseCase(session_provider),
        "get_status": GetStatusUseCase(session_provider),
        "autosave": AutosaveUseCase(session_provider, pyboy, save_repository),
        "manual_save": ManualSaveUseCase(session_provider, pyboy, save_repository),
        "resolve_vote": ResolveVoteUseCase(session_provider),
    }

    scheduler = Scheduler(logger)
    scheduler.register(
        TickTask(use_cases["tick_emulator"], _FRAME_INTERVAL, logger)  # type: ignore[arg-type]
    )
    scheduler.register(
        AutosaveTask(
            use_cases["autosave"],  # type: ignore[arg-type]
            session_config.autosave_interval,
            logger,  # type: ignore[arg-type]
        )
    )
    scheduler.register(
        ResolveVoteTask(
            use_cases["resolve_vote"],  # type: ignore[arg-type]
            session_config.voting_interval,
            logger,  # type: ignore[arg-type]
        )
    )
    scheduler.register(
        MetricsTask(use_cases["collect_metrics"], _METRICS_INTERVAL, logger)  # type: ignore[arg-type]
    )
    scheduler.register(
        HealthCheckTask(use_cases["health_check"], _HEALTH_CHECK_INTERVAL, logger)  # type: ignore[arg-type]
    )

    app = web.Application()
    app["publisher"] = publisher
    app["scheduler"] = scheduler
    app["pyboy"] = pyboy

    setup_middleware(app, logger)
    register_routes(app, use_cases, logger)

    app.on_startup.append(_make_startup(logger, scheduler))
    app.on_shutdown.append(
        _make_shutdown(logger, scheduler, publisher, save_repository, pyboy)
    )

    return app


def _setup_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )


def _make_startup(
    logger: LoggerAdapter,
    scheduler: Scheduler,
) -> Callable[[web.Application], Awaitable[None]]:
    async def startup(app: web.Application) -> None:
        await logger.info("scheduler_starting")
        scheduler.start()
        await logger.info("application_started")

    return startup


def _make_shutdown(
    logger: LoggerAdapter,
    scheduler: Scheduler,
    publisher: AiortcVideoPublisher,
    save_repository: FileSaveRepository,
    pyboy: PyBoyAdapter,
) -> Callable[[web.Application], Awaitable[None]]:
    async def shutdown(app: web.Application) -> None:
        await logger.info("application_stopping")
        await scheduler.stop()
        await publisher.close()
        await logger.info("final_snapshot")
        try:
            data = await pyboy.create_snapshot()
            await save_repository.save(data)
        except Exception:
            await logger.error("final_snapshot_failed", exc_info=True)
        await logger.info("pyboy_releasing")
        pyboy._executor.shutdown(wait=True)  # type: ignore[attr-defined]
        await logger.info("application_stopped")

    return shutdown
