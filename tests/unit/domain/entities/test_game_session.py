from datetime import timedelta
from uuid import uuid4

import pytest

from tests.helpers.factories import make_game_input, make_player_id, make_session

from consumer.domain.entities.game_session import GameSession
from consumer.domain.entities.player import Player
from consumer.domain.enums import Button, ControlMode, SessionState
from consumer.domain.exceptions import (
    PlayerNotConnectedException,
    SessionNotRunningException,
)
from consumer.domain.value_objects import SessionConfiguration, SessionId


class TestGameSessionStateTransitions:
    def test_initial_state(self) -> None:
        session = make_session()
        assert session.current_state == SessionState.STARTING

    def test_start(self) -> None:
        session = make_session()
        session.start()
        assert session.current_state == SessionState.RUNNING

    def test_stop(self) -> None:
        session = make_session()
        session.start()
        session.stop()
        assert session.current_state == SessionState.STOPPED

    def test_pause(self) -> None:
        session = make_session()
        session.start()
        session.pause()
        assert session.current_state == SessionState.PAUSED

    def test_resume(self) -> None:
        session = make_session()
        session.start()
        session.pause()
        session.resume()
        assert session.current_state == SessionState.RUNNING

    def test_full_lifecycle(self) -> None:
        session = make_session()
        session.start()
        session.pause()
        session.resume()
        session.stop()
        assert session.current_state == SessionState.STOPPED


class TestGameSessionPlayers:
    def test_connect_player(self) -> None:
        session = make_session()
        p = Player(player_id=make_player_id(), display_name="Alice")
        session.connect_player(p)
        assert session.players.count == 1
        assert session.metrics.connected_players == 1

    def test_disconnect_player(self) -> None:
        session = make_session()
        pid = make_player_id()
        p = Player(player_id=pid, display_name="Alice")
        session.connect_player(p)
        session.disconnect_player(pid)
        assert session.players.count == 0
        assert session.metrics.connected_players == 0

    def test_disconnect_unknown_raises(self) -> None:
        session = make_session()
        with pytest.raises(PlayerNotConnectedException):
            session.disconnect_player(make_player_id())


class TestGameSessionSubmitInput:
    def test_fifo_enqueue(self) -> None:
        session = make_session(control_mode=ControlMode.FIFO)
        session.start()
        gi = make_game_input()
        session.submit_input(gi)
        assert session.input_queue.size == 1
        assert session.metrics.total_commands == 1

    def test_fifo_multiple_inputs(self) -> None:
        session = make_session(control_mode=ControlMode.FIFO)
        session.start()
        gi1 = make_game_input(Button.LEFT)
        gi2 = make_game_input(Button.RIGHT)
        session.submit_input(gi1)
        session.submit_input(gi2)
        assert session.input_queue.size == 2
        assert session.metrics.total_commands == 2

    def test_voting_collects_vote(self) -> None:
        session = make_session(control_mode=ControlMode.VOTING)
        session.start()
        pid = make_player_id()
        gi = make_game_input(player_id=pid)
        session.submit_input(gi)
        assert session.current_vote is not None
        assert session.current_vote.votes[pid] is gi
        assert session.metrics.total_commands == 1

    def test_voting_multiple_votes(self) -> None:
        session = make_session(control_mode=ControlMode.VOTING)
        session.start()
        pid1 = make_player_id()
        pid2 = make_player_id()
        session.submit_input(make_game_input(Button.LEFT, pid1))
        session.submit_input(make_game_input(Button.RIGHT, pid2))
        assert session.current_vote is not None
        assert len(session.current_vote.votes) == 2

    def test_submit_when_not_running_raises(self) -> None:
        session = make_session()
        with pytest.raises(SessionNotRunningException):
            session.submit_input(make_game_input())


class TestGameSessionControlMode:
    def test_change_to_voting(self) -> None:
        session = make_session(control_mode=ControlMode.FIFO)
        session.change_control_mode(ControlMode.VOTING)
        assert session.configuration.control_mode == ControlMode.VOTING

    def test_change_to_fifo_clears_vote(self) -> None:
        session = make_session(control_mode=ControlMode.VOTING)
        session.start()
        session.submit_input(make_game_input())
        assert session.current_vote is not None
        session.change_control_mode(ControlMode.FIFO)
        assert session.current_vote is None

    def test_change_to_same_mode_is_noop(self) -> None:
        session = make_session(control_mode=ControlMode.FIFO)
        original = session.configuration
        session.change_control_mode(ControlMode.FIFO)
        assert session.configuration is original


class TestGameSessionSnapshot:
    def test_create_snapshot(self) -> None:
        session = make_session()
        session.create_snapshot()
        assert session.save_manager.has_pending_snapshot is True

    def test_restore_snapshot(self) -> None:
        session = make_session()
        session.create_snapshot()
        session.restore_snapshot()
        assert session.save_manager.has_pending_snapshot is False


class TestGameSessionProperties:
    def test_session_id(self) -> None:
        sid = SessionId(value=uuid4())
        config = SessionConfiguration(
            control_mode=ControlMode.FIFO,
            voting_interval=timedelta(seconds=1),
            autosave_interval=timedelta(seconds=15),
        )
        session = GameSession(session_id=sid, configuration=config)
        assert session.session_id == sid

    def test_configuration(self) -> None:
        session = make_session(control_mode=ControlMode.VOTING)
        assert session.configuration.control_mode == ControlMode.VOTING
