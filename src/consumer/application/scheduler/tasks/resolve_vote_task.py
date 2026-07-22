from __future__ import annotations

from datetime import timedelta

from consumer.application.dto.voting import ResolveVoteRequest
from consumer.application.ports.logger_port import LoggerPort
from consumer.application.scheduler.scheduled_task import ScheduledTask
from consumer.application.use_cases.voting_use_cases import (
    ResolveVoteUseCase,
)
from consumer.domain.entities.game_session import GameSession


class ResolveVoteTask(ScheduledTask):
    wall_clock_align = True

    def __init__(
        self,
        use_case: ResolveVoteUseCase,
        session: GameSession,
        logger: LoggerPort,
    ) -> None:
        self._use_case = use_case
        self._session = session
        self._logger = logger

    @property
    def name(self) -> str:
        return "resolve_vote"

    @property
    def interval(self) -> timedelta:
        return self._session.configuration.voting_interval

    async def execute(self) -> None:
        await self._use_case.execute(ResolveVoteRequest())
