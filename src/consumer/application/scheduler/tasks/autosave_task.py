from __future__ import annotations

from datetime import timedelta

from consumer.application.dto.save import AutosaveRequest
from consumer.application.ports.logger_port import LoggerPort
from consumer.application.scheduler.scheduled_task import ScheduledTask
from consumer.application.use_cases.save_use_cases import AutosaveUseCase


class AutosaveTask(ScheduledTask):
    def __init__(
        self,
        use_case: AutosaveUseCase,
        interval: timedelta,
        logger: LoggerPort,
    ) -> None:
        self._use_case = use_case
        self._interval = interval
        self._logger = logger

    @property
    def name(self) -> str:
        return "autosave"

    @property
    def interval(self) -> timedelta:
        return self._interval

    async def execute(self) -> None:
        await self._use_case.execute(AutosaveRequest())
