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


class SlowTask(ScheduledTask):
    def __init__(self) -> None:
        self._interval = timedelta(milliseconds=50)
        self.execute_count = 0

    @property
    def name(self) -> str:
        return "slow"

    @property
    def interval(self) -> timedelta:
        return self._interval

    async def execute(self) -> None:
        await asyncio.sleep(0.1)
        self.execute_count += 1


class FailingAlternatingTask(ScheduledTask):
    def __init__(self) -> None:
        self._interval = timedelta(milliseconds=50)
        self.execute_count = 0

    @property
    def name(self) -> str:
        return "flaky"

    @property
    def interval(self) -> timedelta:
        return self._interval

    async def execute(self) -> None:
        self.execute_count += 1
        if self.execute_count % 2 == 0:
            raise RuntimeError("transient failure")


class TestSchedulerIntegration:
    async def test_multi_task_concurrent(self) -> None:
        logger = StubLogger()
        scheduler = Scheduler(logger)
        t1 = StubTask("a", interval_ms=10)
        t2 = StubTask("b", interval_ms=10)
        t3 = StubTask("c", interval_ms=10)
        scheduler.register(t1)
        scheduler.register(t2)
        scheduler.register(t3)

        scheduler.start()
        await asyncio.sleep(1)
        await scheduler.stop()

        assert t1.execute_count >= 20
        assert t2.execute_count >= 20
        assert t3.execute_count >= 20

    async def test_task_recovers_after_failure(self) -> None:
        logger = StubLogger()
        scheduler = Scheduler(logger)
        task = FailingAlternatingTask()
        scheduler.register(task)

        scheduler.start()
        await asyncio.sleep(0.5)
        await scheduler.stop()

        assert task.execute_count >= 5

    async def test_interval_timing(self) -> None:
        logger = StubLogger()
        scheduler = Scheduler(logger)
        task = StubTask("timed", interval_ms=50)
        scheduler.register(task)

        scheduler.start()
        await asyncio.sleep(0.5)
        await scheduler.stop()

        assert 7 <= task.execute_count <= 13

    async def test_slow_task_does_not_block_fast(self) -> None:
        logger = StubLogger()
        scheduler = Scheduler(logger)
        slow = SlowTask()
        fast = StubTask("fast", interval_ms=10)
        scheduler.register(slow)
        scheduler.register(fast)

        scheduler.start()
        await asyncio.sleep(1)
        await scheduler.stop()

        assert fast.execute_count >= slow.execute_count * 5

    async def test_stop_cancels_running_tasks(self) -> None:
        logger = StubLogger()
        scheduler = Scheduler(logger)

        class BlockingTask(ScheduledTask):
            def __init__(self) -> None:
                self._interval = timedelta(seconds=10)
                self.invoked = False
                self._started = asyncio.Event()

            @property
            def name(self) -> str:
                return "blocker"

            @property
            def interval(self) -> timedelta:
                return self._interval

            async def execute(self) -> None:
                self.invoked = True
                self._started.set()
                await asyncio.sleep(10)

        task = BlockingTask()
        scheduler.register(task)

        scheduler.start()
        await task._started.wait()
        assert task.invoked is True

        await scheduler.stop()

        assert scheduler._running is False
        assert len(scheduler._asyncio_tasks) == 0
