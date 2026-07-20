from __future__ import annotations

from consumer.application.dto.voting import (
    ResolveVoteRequest,
    ResolveVoteResponse,
)
from consumer.application.mappers.voting_mapper import VotingMapper
from consumer.application.ports.game_session_provider import GameSessionProvider
from consumer.domain.services.vote_resolver import VoteResolver


class ResolveVoteUseCase:
    def __init__(self, session_provider: GameSessionProvider) -> None:
        self._session_provider = session_provider

    async def execute(
        self,
        request: ResolveVoteRequest,  # noqa: ARG002
    ) -> ResolveVoteResponse:
        session = await self._session_provider.get_session()
        vote_round = session.current_vote
        if vote_round is None:
            return ResolveVoteResponse()
        result = VoteResolver.resolve(vote_round)
        session.resolve_vote()
        return VotingMapper.to_resolve_vote_response(result)
