from datetime import datetime, timezone
from uuid import uuid4

from consumer.application.mappers.voting_mapper import VotingMapper
from consumer.domain.enums import Button
from consumer.domain.value_objects import GameInput, PlayerId, VoteResult


class TestVotingMapper:
    def test_to_resolve_vote_response(self) -> None:
        pid = uuid4()
        now = datetime.now(tz=timezone.utc)
        winning = GameInput(
            button=Button.A, timestamp=now, player_id=PlayerId(value=pid)
        )
        result = VoteResult(winning_input=winning, vote_count=5)

        resp = VotingMapper.to_resolve_vote_response(result)

        assert resp.winning_button == Button.A
        assert resp.vote_count == 5

    def test_to_resolve_vote_response_single_vote(self) -> None:
        pid = uuid4()
        now = datetime.now(tz=timezone.utc)
        winning = GameInput(
            button=Button.B, timestamp=now, player_id=PlayerId(value=pid)
        )
        result = VoteResult(winning_input=winning, vote_count=1)

        resp = VotingMapper.to_resolve_vote_response(result)

        assert resp.winning_button == Button.B
        assert resp.vote_count == 1
