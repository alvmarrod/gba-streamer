from __future__ import annotations

import asyncio
from datetime import timedelta

from consumer.application.scheduler.scheduled_task import ScheduledTask
from consumer.application.scheduler.scheduler import Scheduler

from tests.helpers.stub_providers import StubLogger


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
        self._interval = timedelta(milliseconds=10)
        self.execute_count = 0

    @property
    def name(self) -> str:
        return "failing"

    @property
    def interval(self) -> timedelta:
        return self._interval

    async def execute(self) -> None:
        self.execute_count += 1
        raise RuntimeError("failure")


class TestSchedulerReliability:
    async def test_30s_multi_task(self) -> None:
        logger = StubLogger()
        scheduler = Scheduler(logger)
        t1 = StubTask("a", interval_ms=10)
        t2 = StubTask("b", interval_ms=10)
        t3 = StubTask("c", interval_ms=10)
        scheduler.register(t1)
        scheduler.register(t2)
        scheduler.register(t3)

        scheduler.start()
        await asyncio.sleep(30)
        await scheduler.stop()

        assert t1.execute_count >= 2000
        assert t2.execute_count >= 2000
        assert t3.execute_count >= 2000

    async def test_30s_with_failing(self) -> None:
        logger = StubLogger()
        scheduler = Scheduler(logger)
        failing = FailingTask()
        good1 = StubTask("good1", interval_ms=10)
        good2 = StubTask("good2", interval_ms=10)
        scheduler.register(failing)
        scheduler.register(good1)
        scheduler.register(good2)

        scheduler.start()
        await asyncio.sleep(30)
        await scheduler.stop()

        assert failing.execute_count >= 2000
        assert good1.execute_count >= 2000
        assert good2.execute_count >= 2000
