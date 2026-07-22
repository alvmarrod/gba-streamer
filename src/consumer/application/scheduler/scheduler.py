from __future__ import annotations

import asyncio
import math
import time

from consumer.application.ports.logger_port import LoggerPort
from consumer.application.scheduler.scheduled_task import ScheduledTask


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

    async def stop(self) -> None:
        self._running = False
        for t in self._asyncio_tasks:
            t.cancel()
        await asyncio.gather(*self._asyncio_tasks, return_exceptions=True)
        self._asyncio_tasks.clear()

    async def _run_loop(self, task: ScheduledTask) -> None:
        interval_secs = task.interval.total_seconds()
        if task.wall_clock_align:
            now = time.monotonic()
            deadline = math.ceil(now / interval_secs) * interval_secs
        else:
            deadline = None

        while self._running:
            try:
                await task.execute()
            except Exception:
                await self._logger.error(f"Task {task.name} failed", exc_info=True)

            if deadline is not None:
                deadline += interval_secs
                now = time.monotonic()
                if deadline > now:
                    await asyncio.sleep(deadline - now)
            else:
                await asyncio.sleep(interval_secs)
