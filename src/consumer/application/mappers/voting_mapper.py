from __future__ import annotations

from consumer.domain.value_objects import VoteResult

from consumer.application.dto.voting import ResolveVoteResponse


class VotingMapper:
    @staticmethod
    def to_resolve_vote_response(result: VoteResult) -> ResolveVoteResponse:
        return ResolveVoteResponse(
            winning_button=result.winning_input.button,
            vote_count=result.vote_count,
        )
