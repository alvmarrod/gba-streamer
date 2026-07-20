from __future__ import annotations

from datetime import timedelta

from consumer.application.dto.monitoring import CollectMetricsRequest
from consumer.application.ports.logger_port import LoggerPort
from consumer.application.scheduler.scheduled_task import ScheduledTask
from consumer.application.use_cases.monitoring_use_cases import (
    CollectMetricsUseCase,
)


class MetricsTask(ScheduledTask):
    def __init__(
        self,
        use_case: CollectMetricsUseCase,
        interval: timedelta,
        logger: LoggerPort,
    ) -> None:
        self._use_case = use_case
        self._interval = interval
        self._logger = logger

    @property
    def name(self) -> str:
        return "metrics"

    @property
    def interval(self) -> timedelta:
        return self._interval

    async def execute(self) -> None:
        await self._use_case.execute(CollectMetricsRequest(), elapsed=self._interval)
