from __future__ import annotations

import asyncio
import logging
import os
import sys
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
from consumer.application.dto.monitoring import CollectMetricsRequest
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
from consumer.application.use_cases.telegram_command_use_case import (
    HandleTelegramCommandUseCase,
)
from consumer.application.use_cases.voting_use_cases import ResolveVoteUseCase
from consumer.domain.entities.game_session import GameSession
from consumer.domain.enums import ControlMode
from consumer.domain.value_objects import SessionConfiguration, SessionId
from consumer.infrastructure.authorization.env_admin_authorizer import (
    EnvAdminAuthorizer,
)
from consumer.infrastructure.configuration.file_configuration_provider import (
    FileConfigurationProvider,
)
from consumer.infrastructure.emulator.pyboy_adapter import PyBoyAdapter
from consumer.infrastructure.health.composite_indicator import (
    CompositeHealthIndicator,
)
from consumer.infrastructure.monitoring.json_formatter import JsonFormatter
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
from consumer.infrastructure.streaming.ice_config import IceConfigProvider
from consumer.infrastructure.telegram.rabbitmq_adapter import (
    RabbitMQTelegramAdapter,
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

    start_session_uc = StartSessionUseCase(session_provider)
    stop_session_uc = StopSessionUseCase(session_provider)
    pause_session_uc = PauseSessionUseCase(session_provider)
    resume_session_uc = ResumeSessionUseCase(session_provider)
    change_control_mode_uc = ChangeControlModeUseCase(session_provider)
    get_status_uc = GetStatusUseCase(session_provider)

    metrics_publisher = MetricsPublisher(logger)

    telegram_adapter = RabbitMQTelegramAdapter()
    authorizer = EnvAdminAuthorizer()
    telegram_command_uc = HandleTelegramCommandUseCase(
        start_session_uc,
        stop_session_uc,
        pause_session_uc,
        resume_session_uc,
        change_control_mode_uc,
        get_status_uc,
        telegram_adapter,
        authorizer,
    )

    scheduler = Scheduler(logger)

    health_indicator = CompositeHealthIndicator(
        scheduler, pyboy, save_repository, publisher
    )

    use_cases: dict[str, object] = {
        "start_session": start_session_uc,
        "stop_session": stop_session_uc,
        "pause_session": pause_session_uc,
        "resume_session": resume_session_uc,
        "restore_session": RestoreSessionUseCase(
            session_provider, pyboy, save_repository
        ),
        "connect_player": ConnectPlayerUseCase(session_provider),
        "disconnect_player": DisconnectPlayerUseCase(session_provider),
        "submit_input": SubmitInputUseCase(session_provider),
        "resolve_input": ResolveInputUseCase(session_provider, pyboy),
        "tick_emulator": TickEmulatorUseCase(session_provider, pyboy, publisher),
        "change_control_mode": change_control_mode_uc,
        "reload_configuration": ReloadConfigurationUseCase(
            session_provider, config_provider
        ),
        "collect_metrics": CollectMetricsUseCase(session_provider, metrics_publisher),
        "health_check": HealthCheckUseCase(
            session_provider, health_indicator=health_indicator
        ),
        "get_status": get_status_uc,
        "autosave": AutosaveUseCase(session_provider, pyboy, save_repository),
        "manual_save": ManualSaveUseCase(session_provider, pyboy, save_repository),
        "resolve_vote": ResolveVoteUseCase(session_provider),
    }

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
    app["ice_config"] = IceConfigProvider().configuration
    app["scheduler"] = scheduler
    app["pyboy"] = pyboy
    app["telegram_adapter"] = telegram_adapter
    app["telegram_command"] = telegram_command_uc

    setup_middleware(app, logger)
    register_routes(app, use_cases, logger)

    app.on_startup.append(
        _make_startup(logger, scheduler, telegram_adapter, telegram_command_uc)
    )
    app.on_shutdown.append(
        _make_shutdown(
            logger,
            scheduler,
            publisher,
            save_repository,
            pyboy,
            telegram_adapter,
            use_cases["collect_metrics"],  # type: ignore[arg-type]
        )
    )

    return app


def _setup_logging() -> None:
    level = os.environ.get("LOG_LEVEL", "INFO").upper()
    handler = logging.StreamHandler(sys.stderr)
    handler.setFormatter(JsonFormatter())
    logging.basicConfig(level=level, handlers=[handler], force=True)


def _make_startup(
    logger: LoggerAdapter,
    scheduler: Scheduler,
    telegram_adapter: RabbitMQTelegramAdapter,
    telegram_command: HandleTelegramCommandUseCase,
) -> Callable[[web.Application], Awaitable[None]]:
    async def startup(app: web.Application) -> None:
        await telegram_adapter.connect()
        await telegram_adapter.subscribe(telegram_command.execute)
        consumer_task = asyncio.create_task(telegram_adapter.start())
        app["_consumer_task"] = consumer_task
        await logger.info("telegram_connected")

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
    telegram_adapter: RabbitMQTelegramAdapter,
    collect_metrics: CollectMetricsUseCase,
) -> Callable[[web.Application], Awaitable[None]]:
    async def shutdown(app: web.Application) -> None:
        await logger.info("application_stopping")

        consumer_task: asyncio.Task[None] | None = app.get("_consumer_task")  # type: ignore[assignment]
        if consumer_task is not None:
            consumer_task.cancel()
            try:
                await consumer_task
            except asyncio.CancelledError:
                pass
        await telegram_adapter.close()
        await logger.info("telegram_disconnected")

        await scheduler.stop()
        await publisher.close()

        await logger.info("flushing_metrics")
        try:
            await collect_metrics.execute(CollectMetricsRequest())
        except Exception:
            pass

        await logger.info("final_snapshot")
        try:
            data = await pyboy.create_snapshot()
            await save_repository.save(data)
        except Exception:
            await logger.error("final_snapshot_failed", exc_info=True)
        await logger.info("pyboy_releasing")
        pyboy._executor.shutdown(wait=True)  # type: ignore[attr-defined]
        await logger.info("application_stopped")
        logging.shutdown()

    return shutdown
