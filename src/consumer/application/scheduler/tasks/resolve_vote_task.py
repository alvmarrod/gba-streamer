from __future__ import annotations

from datetime import timedelta

from consumer.application.dto.voting import ResolveVoteRequest
from consumer.application.ports.logger_port import LoggerPort
from consumer.application.scheduler.scheduled_task import ScheduledTask
from consumer.application.use_cases.voting_use_cases import (
    ResolveVoteUseCase,
)


class ResolveVoteTask(ScheduledTask):
    def __init__(
        self,
        use_case: ResolveVoteUseCase,
        interval: timedelta,
        logger: LoggerPort,
    ) -> None:
        self._use_case = use_case
        self._interval = interval
        self._logger = logger

    @property
    def name(self) -> str:
        return "resolve_vote"

    @property
    def interval(self) -> timedelta:
        return self._interval

    async def execute(self) -> None:
        await self._use_case.execute(ResolveVoteRequest())
