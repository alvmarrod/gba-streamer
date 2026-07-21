from datetime import datetime
from uuid import uuid4

import pytest

from consumer.domain.composed.exceptions import InvalidSessionStateException
from consumer.domain.composed.vote_round import VoteRound
from consumer.domain.enums import Button
from consumer.domain.value_objects import GameInput, PlayerId


def _make_player_id() -> PlayerId:
    return PlayerId(value=uuid4())


def _make_game_input(button: Button = Button.A) -> GameInput:
    return GameInput(
        button=button,
        timestamp=datetime(2026, 1, 1, 12, 0, 0),
        player_id=_make_player_id(),
    )


class TestVoteRound:
    def test_initially_open(self) -> None:
        assert VoteRound().is_open is True

    def test_initially_empty(self) -> None:
        assert VoteRound().votes == {}

    def test_collect_vote(self) -> None:
        vr = VoteRound()
        pid = _make_player_id()
        gi = _make_game_input()
        vr.collect_vote(pid, gi)
        assert vr.votes[pid] is gi

    def test_collect_vote_overwrites_same_player(self) -> None:
        vr = VoteRound()
        pid = _make_player_id()
        first = _make_game_input(Button.LEFT)
        second = _make_game_input(Button.RIGHT)
        vr.collect_vote(pid, first)
        vr.collect_vote(pid, second)
        assert vr.votes[pid] is second
        assert len(vr.votes) == 1

    def test_collect_multiple_players(self) -> None:
        vr = VoteRound()
        pid1 = _make_player_id()
        pid2 = _make_player_id()
        vr.collect_vote(pid1, _make_game_input(Button.LEFT))
        vr.collect_vote(pid2, _make_game_input(Button.RIGHT))
        assert len(vr.votes) == 2

    def test_collect_after_close_raises(self) -> None:
        vr = VoteRound()
        vr.close()
        with pytest.raises(InvalidSessionStateException, match="closed"):
            vr.collect_vote(_make_player_id(), _make_game_input())

    def test_close(self) -> None:
        vr = VoteRound()
        vr.close()
        assert vr.is_open is False

    def test_votes_returns_copy(self) -> None:
        vr = VoteRound()
        pid = _make_player_id()
        vr.collect_vote(pid, _make_game_input())
        votes = vr.votes
        votes.clear()
        assert len(vr.votes) == 1

    def test_initially_not_applied(self) -> None:
        assert VoteRound().applied is False

    def test_mark_applied(self) -> None:
        vr = VoteRound()
        vr.mark_applied()
        assert vr.applied is True
