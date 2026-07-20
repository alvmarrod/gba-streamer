from __future__ import annotations

import asyncio
from datetime import timedelta


from consumer.application.ports.logger_port import LoggerPort
from consumer.application.scheduler.scheduled_task import ScheduledTask
from consumer.application.scheduler.scheduler import Scheduler


class StubLogger(LoggerPort):
    async def debug(self, message: str, **kwargs: object) -> None:
        pass

    async def info(self, message: str, **kwargs: object) -> None:
        pass

    async def warning(self, message: str, **kwargs: object) -> None:
        pass

    async def error(self, message: str, **kwargs: object) -> None:
        pass


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
