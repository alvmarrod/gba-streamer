from __future__ import annotations

import asyncio
import math
import time
from dataclasses import dataclass

from consumer.application.ports.logger_port import LoggerPort
from consumer.application.scheduler.scheduled_task import ScheduledTask


@dataclass(frozen=True)
class StopResult:
    timed_out: bool
    pending_count: int


class Scheduler:
    def __init__(self, logger: LoggerPort) -> None:
        self._tasks: list[ScheduledTask] = []
        self._asyncio_tasks: list[asyncio.Task[None]] = []
        self._logger = logger
        self._running = False

    @property
    def task_count(self) -> int:
        return len(self._tasks)

    def register(self, task: ScheduledTask) -> None:
        self._tasks.append(task)

    def start(self) -> None:
        self._running = True
        for task in self._tasks:
            self._asyncio_tasks.append(asyncio.create_task(self._run_loop(task)))

    async def stop(self, timeout: float = 5.0) -> StopResult:
        self._running = False
        for t in self._asyncio_tasks:
            t.cancel()
        if not self._asyncio_tasks:
            self._asyncio_tasks.clear()
            return StopResult(timed_out=False, pending_count=0)
        _, pending = await asyncio.wait(self._asyncio_tasks, timeout=timeout)
        if pending:
            await self._logger.error(
                "scheduler_stop_timeout",
                pending_count=len(pending),
            )
        self._asyncio_tasks.clear()
        return StopResult(timed_out=bool(pending), pending_count=len(pending))

    async def _run_loop(self, task: ScheduledTask) -> None:
        now = time.monotonic()
        if task.wall_clock_align:
            interval_secs = task.interval.total_seconds()
            next_run = math.ceil(now / interval_secs) * interval_secs
        else:
            next_run = now

        while self._running:
            if not task.wall_clock_align:
                next_run += task.interval.total_seconds()

            try:
                await task.execute()
            except asyncio.CancelledError:
                return
            except Exception:
                await self._logger.error(f"Task {task.name} failed", exc_info=True)

            sleep_time = next_run - time.monotonic()
            if sleep_time > 0:
                try:
                    await asyncio.sleep(sleep_time)
                except asyncio.CancelledError:
                    return
            elif sleep_time < 0:
                await self._logger.warning(
                    f"Task {task.name} overran by {-sleep_time * 1000:.1f}ms"
                )

            if task.wall_clock_align:
                interval_secs = task.interval.total_seconds()
                next_run += interval_secs
                if time.monotonic() > next_run:
                    now = time.monotonic()
                    next_run = math.ceil(now / interval_secs) * interval_secs
