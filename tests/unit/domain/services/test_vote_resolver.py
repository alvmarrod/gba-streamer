from datetime import datetime, timezone
from uuid import uuid4

from consumer.domain.composed.vote_round import VoteRound
from consumer.domain.enums import Button
from consumer.domain.services.vote_resolver import VoteResolver
from consumer.domain.value_objects import GameInput, PlayerId


class TestVoteResolver:
    def test_clear_winner(self) -> None:
        vote_round = VoteRound()
        now = datetime.now(tz=timezone.utc)
        p1 = PlayerId(uuid4())
        p2 = PlayerId(uuid4())
        p3 = PlayerId(uuid4())

        vote_round.collect_vote(
            p1, GameInput(button=Button.A, timestamp=now, player_id=p1)
        )
        vote_round.collect_vote(
            p2, GameInput(button=Button.A, timestamp=now, player_id=p2)
        )
        vote_round.collect_vote(
            p3, GameInput(button=Button.B, timestamp=now, player_id=p3)
        )

        result = VoteResolver.resolve(vote_round)

        assert result.winning_input.button == Button.A
        assert result.vote_count == 2

    def test_tie_first_vote_wins(self) -> None:
        vote_round = VoteRound()
        now = datetime.now(tz=timezone.utc)
        p1 = PlayerId(uuid4())
        p2 = PlayerId(uuid4())

        input_a = GameInput(button=Button.A, timestamp=now, player_id=p1)
        input_b = GameInput(button=Button.B, timestamp=now, player_id=p2)

        vote_round.collect_vote(p1, input_a)
        vote_round.collect_vote(p2, input_b)

        result = VoteResolver.resolve(vote_round)

        assert result.winning_input is input_a
        assert result.vote_count == 1

    def test_single_vote(self) -> None:
        vote_round = VoteRound()
        now = datetime.now(tz=timezone.utc)
        p1 = PlayerId(uuid4())

        game_input = GameInput(button=Button.LEFT, timestamp=now, player_id=p1)
        vote_round.collect_vote(p1, game_input)

        result = VoteResolver.resolve(vote_round)

        assert result.winning_input is game_input
        assert result.vote_count == 1
