from datetime import timedelta
from uuid import uuid4

import pytest

from consumer.domain.entities.game_session import GameSession
from consumer.domain.entities.player import Player
from consumer.domain.enums import ControlMode
from consumer.domain.services.session_validator import SessionValidator
from consumer.domain.value_objects import (
    PlayerId,
    SessionConfiguration,
    SessionId,
)


def _make_session(control_mode: ControlMode = ControlMode.FIFO) -> GameSession:
    return GameSession(
        session_id=SessionId(uuid4()),
        configuration=SessionConfiguration(
            control_mode=control_mode,
            voting_interval=timedelta(seconds=30),
            autosave_interval=timedelta(minutes=5),
        ),
    )


def _connect_player(session: GameSession) -> Player:
    player = Player(player_id=PlayerId(uuid4()), display_name="test")
    session.connect_player(player)
    return player


class TestSessionValidator:
    def test_valid_session_passes(self) -> None:
        session = _make_session()
        SessionValidator.validate(session)

    def test_player_count_mismatch_raises(self) -> None:
        session = _make_session()
        session._metrics._connected_players = 5

        with pytest.raises(ValueError, match="Player count mismatch"):
            SessionValidator.validate(session)

    def test_total_players_seen_less_than_connected_raises(self) -> None:
        session = _make_session()
        _connect_player(session)
        _connect_player(session)

        session._metrics._total_players_seen = 1

        with pytest.raises(ValueError, match="total_players_seen"):
            SessionValidator.validate(session)

    def test_fifo_mode_with_vote_round_raises(self) -> None:
        from consumer.domain.composed.vote_round import VoteRound

        session = _make_session(control_mode=ControlMode.FIFO)
        session._current_vote = VoteRound()

        with pytest.raises(ValueError, match="FIFO mode active"):
            SessionValidator.validate(session)
