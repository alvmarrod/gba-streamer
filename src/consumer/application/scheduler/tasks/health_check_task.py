from __future__ import annotations

from datetime import timedelta

from consumer.application.dto.monitoring import HealthCheckRequest
from consumer.application.ports.logger_port import LoggerPort
from consumer.application.scheduler.scheduled_task import ScheduledTask
from consumer.application.use_cases.monitoring_use_cases import (
    HealthCheckUseCase,
)


class HealthCheckTask(ScheduledTask):
    def __init__(
        self,
        use_case: HealthCheckUseCase,
        interval: timedelta,
        logger: LoggerPort,
    ) -> None:
        self._use_case = use_case
        self._interval = interval
        self._logger = logger

    @property
    def name(self) -> str:
        return "health_check"

    @property
    def interval(self) -> timedelta:
        return self._interval

    async def execute(self) -> None:
        await self._use_case.execute(HealthCheckRequest())
