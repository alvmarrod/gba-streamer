from __future__ import annotations

from datetime import timedelta
from unittest.mock import AsyncMock, MagicMock


from consumer.application.dto.gameplay import TickEmulatorRequest
from consumer.application.dto.monitoring import (
    CollectMetricsRequest,
    HealthCheckRequest,
)
from consumer.application.dto.save import AutosaveRequest
from consumer.application.dto.voting import ResolveVoteRequest
from consumer.application.ports.logger_port import LoggerPort
from consumer.application.scheduler.tasks.autosave_task import AutosaveTask
from consumer.application.scheduler.tasks.health_check_task import (
    HealthCheckTask,
)
from consumer.application.scheduler.tasks.metrics_task import MetricsTask
from consumer.application.scheduler.tasks.resolve_vote_task import (
    ResolveVoteTask,
)
from consumer.application.scheduler.tasks.tick_task import TickTask
from consumer.application.use_cases.gameplay_use_cases import (
    TickEmulatorUseCase,
)
from consumer.application.use_cases.monitoring_use_cases import (
    CollectMetricsUseCase,
    HealthCheckUseCase,
)
from consumer.application.use_cases.save_use_cases import AutosaveUseCase
from consumer.application.use_cases.voting_use_cases import (
    ResolveVoteUseCase,
)


class StubLogger(LoggerPort):
    async def debug(self, message: str, **kwargs: object) -> None:
        pass

    async def info(self, message: str, **kwargs: object) -> None:
        pass

    async def warning(self, message: str, **kwargs: object) -> None:
        pass

    async def error(self, message: str, **kwargs: object) -> None:
        pass


class TestTickTask:
    async def test_calls_use_case(self) -> None:
        use_case = AsyncMock(spec=TickEmulatorUseCase)
        logger = StubLogger()
        task = TickTask(
            use_case=use_case,
            interval=timedelta(seconds=1),
            logger=logger,
        )

        assert task.name == "tick"
        assert task.interval == timedelta(seconds=1)

        await task.execute()

        use_case.execute.assert_awaited_once()
        arg = use_case.execute.call_args[0][0]
        assert isinstance(arg, TickEmulatorRequest)


def _make_session_mock(
    autosave: timedelta = timedelta(minutes=5),
    voting: timedelta = timedelta(seconds=30),
) -> MagicMock:
    from consumer.domain.value_objects import SessionConfiguration
    from consumer.domain.enums import ControlMode

    config = SessionConfiguration(
        control_mode=ControlMode.FIFO,
        voting_interval=voting,
        autosave_interval=autosave,
    )
    session = MagicMock()
    session.configuration = config
    return session


class TestAutosaveTask:
    async def test_calls_use_case(self) -> None:
        use_case = AsyncMock(spec=AutosaveUseCase)
        logger = StubLogger()
        session = _make_session_mock(autosave=timedelta(minutes=5))
        task = AutosaveTask(
            use_case=use_case,
            session=session,
            logger=logger,
        )

        assert task.name == "autosave"
        assert task.interval == timedelta(minutes=5)

        await task.execute()

        use_case.execute.assert_awaited_once()
        arg = use_case.execute.call_args[0][0]
        assert isinstance(arg, AutosaveRequest)


class TestResolveVoteTask:
    async def test_calls_use_case(self) -> None:
        use_case = AsyncMock(spec=ResolveVoteUseCase)
        logger = StubLogger()
        session = _make_session_mock(voting=timedelta(seconds=30))
        task = ResolveVoteTask(
            use_case=use_case,
            session=session,
            logger=logger,
        )

        assert task.name == "resolve_vote"
        assert task.interval == timedelta(seconds=30)

        await task.execute()

        use_case.execute.assert_awaited_once()
        arg = use_case.execute.call_args[0][0]
        assert isinstance(arg, ResolveVoteRequest)


class TestMetricsTask:
    async def test_calls_use_case_with_elapsed(self) -> None:
        use_case = AsyncMock(spec=CollectMetricsUseCase)
        logger = StubLogger()
        interval = timedelta(seconds=10)
        task = MetricsTask(
            use_case=use_case,
            interval=interval,
            logger=logger,
        )

        assert task.name == "metrics"
        assert task.interval == timedelta(seconds=10)

        await task.execute()

        use_case.execute.assert_awaited_once()
        arg = use_case.execute.call_args[0][0]
        elapsed = use_case.execute.call_args[1]["elapsed"]
        assert isinstance(arg, CollectMetricsRequest)
        assert elapsed == interval


class TestHealthCheckTask:
    async def test_calls_use_case(self) -> None:
        use_case = AsyncMock(spec=HealthCheckUseCase)
        logger = StubLogger()
        task = HealthCheckTask(
            use_case=use_case,
            interval=timedelta(seconds=30),
            logger=logger,
        )

        assert task.name == "health_check"
        assert task.interval == timedelta(seconds=30)

        await task.execute()

        use_case.execute.assert_awaited_once()
        arg = use_case.execute.call_args[0][0]
        assert isinstance(arg, HealthCheckRequest)
