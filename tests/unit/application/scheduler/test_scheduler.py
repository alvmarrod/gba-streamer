from __future__ import annotations

import asyncio
from datetime import timedelta


from consumer.application.ports.logger_port import LoggerPort
from consumer.application.scheduler.scheduled_task import ScheduledTask
from consumer.application.scheduler.scheduler import Scheduler, StopResult


class StubLogger(LoggerPort):
    async def debug(self, message: str, **kwargs: object) -> None:
        pass

    async def info(self, message: str, **kwargs: object) -> None:
        pass

    async def warning(self, message: str, **kwargs: object) -> None:
        pass

    async def error(self, message: str, **kwargs: object) -> None:
        pass


class CapturingLogger(LoggerPort):
    def __init__(self) -> None:
        self.warnings: list[str] = []
        self.errors: list[str] = []

    async def debug(self, message: str, **kwargs: object) -> None:
        pass

    async def info(self, message: str, **kwargs: object) -> None:
        pass

    async def warning(self, message: str, **kwargs: object) -> None:
        self.warnings.append(message)

    async def error(self, message: str, **kwargs: object) -> None:
        self.errors.append(message)


class StubTask(ScheduledTask):
    def __init__(
        self,
        task_name: str = "stub",
        interval_ms: int = 50,
    ) -> None:
        self._name = task_name
        self._interval = timedelta(milliseconds=interval_ms)
        self.execute_count = 0

    @property
    def name(self) -> str:
        return self._name

    @property
    def interval(self) -> timedelta:
        return self._interval

    async def execute(self) -> None:
        self.execute_count += 1


class FailingTask(ScheduledTask):
    def __init__(self) -> None:
        self._interval = timedelta(milliseconds=50)
        self.execute_count = 0

    @property
    def name(self) -> str:
        return "failing"

    @property
    def interval(self) -> timedelta:
        return self._interval

    async def execute(self) -> None:
        self.execute_count += 1
        raise RuntimeError("task failure")


class TestScheduler:
    async def test_register_adds_task(self) -> None:
        logger = StubLogger()
        scheduler = Scheduler(logger)
        task = StubTask()

        scheduler.register(task)

        assert scheduler.task_count == 1

    async def test_start_executes_tasks(self) -> None:
        logger = StubLogger()
        scheduler = Scheduler(logger)
        task = StubTask(interval_ms=10)
        scheduler.register(task)

        scheduler.start()
        await asyncio.sleep(0.15)
        await scheduler.stop()

        assert task.execute_count >= 1

    async def test_task_failure_does_not_stop_others(self) -> None:
        logger = StubLogger()
        scheduler = Scheduler(logger)
        failing = FailingTask()
        good = StubTask(task_name="good", interval_ms=10)
        scheduler.register(failing)
        scheduler.register(good)

        scheduler.start()
        await asyncio.sleep(0.15)
        await scheduler.stop()

        assert failing.execute_count >= 1
        assert good.execute_count >= 1

    async def test_stop_cancels_all_tasks(self) -> None:
        logger = StubLogger()
        scheduler = Scheduler(logger)
        task = StubTask(interval_ms=10)
        scheduler.register(task)

        scheduler.start()
        await asyncio.sleep(0.05)
        await scheduler.stop()

        assert scheduler._running is False
        assert len(scheduler._asyncio_tasks) == 0

    async def test_empty_scheduler_starts_and_stops(self) -> None:
        logger = StubLogger()
        scheduler = Scheduler(logger)

        scheduler.start()
        await asyncio.sleep(0.01)
        await scheduler.stop()

        assert scheduler.task_count == 0
        assert scheduler._running is False


class SlowTask(ScheduledTask):
    def __init__(self, sleep_s: float = 0.1) -> None:
        self._interval = timedelta(milliseconds=10)
        self._sleep_s = sleep_s
        self.execute_count = 0

    @property
    def name(self) -> str:
        return "slow"

    @property
    def interval(self) -> timedelta:
        return self._interval

    async def execute(self) -> None:
        await asyncio.sleep(self._sleep_s)
        self.execute_count += 1


class TestSchedulerOverrun:
    async def test_overrun_logs_warning(self) -> None:
        logger = CapturingLogger()
        scheduler = Scheduler(logger)
        task = SlowTask(sleep_s=0.05)
        scheduler.register(task)

        scheduler.start()
        await asyncio.sleep(0.3)
        await scheduler.stop()

        assert task.execute_count >= 1
        overrun_warnings = [w for w in logger.warnings if "overran" in w]
        assert len(overrun_warnings) >= 1


class TestSchedulerStopResult:
    async def test_stop_returns_result(self) -> None:
        logger = StubLogger()
        scheduler = Scheduler(logger)
        task = StubTask(interval_ms=10)
        scheduler.register(task)

        scheduler.start()
        await asyncio.sleep(0.05)
        result = await scheduler.stop()

        assert isinstance(result, StopResult)
        assert result.timed_out is False
        assert result.pending_count == 0

    async def test_empty_scheduler_stop_returns_result(self) -> None:
        logger = StubLogger()
        scheduler = Scheduler(logger)

        scheduler.start()
        await asyncio.sleep(0.01)
        result = await scheduler.stop()

        assert isinstance(result, StopResult)
        assert result.timed_out is False
        assert result.pending_count == 0

    async def test_stop_result_dataclass(self) -> None:
        result = StopResult(timed_out=True, pending_count=3)
        assert result.timed_out is True
        assert result.pending_count == 3


class TestSchedulerDeadlineTiming:
    async def test_deadline_scheduling_counts(self) -> None:
        logger = StubLogger()
        scheduler = Scheduler(logger)
        task = StubTask("timed", interval_ms=50)
        scheduler.register(task)

        scheduler.start()
        await asyncio.sleep(0.5)
        await scheduler.stop()

        expected = 10
        assert expected - 2 <= task.execute_count <= expected + 2
