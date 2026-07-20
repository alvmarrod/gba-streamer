from datetime import datetime, timedelta
from uuid import uuid4

import pytest

from consumer.domain.enums import Button, ControlMode
from consumer.domain.value_objects import (
    GameInput,
    PlayerId,
    PlayerStatistics,
    SaveMetadata,
    SessionConfiguration,
    SessionId,
    VoteResult,
)


def _make_player_id() -> PlayerId:
    return PlayerId(value=uuid4())


def _make_session_id() -> SessionId:
    return SessionId(value=uuid4())


def _make_game_input(**overrides: object) -> GameInput:
    defaults = {
        "button": Button.A,
        "timestamp": datetime(2026, 1, 1, 12, 0, 0),
        "player_id": _make_player_id(),
    }
    defaults.update(overrides)
    return GameInput(**defaults)  # type: ignore[arg-type]


class TestSessionId:
    def test_construction(self) -> None:
        uid = uuid4()
        sid = SessionId(value=uid)
        assert sid.value == uid

    def test_immutability(self) -> None:
        sid = _make_session_id()
        with pytest.raises(AttributeError):
            sid.value = uuid4()  # type: ignore[misc]

    def test_equality(self) -> None:
        uid = uuid4()
        assert SessionId(value=uid) == SessionId(value=uid)

    def test_inequality(self) -> None:
        assert _make_session_id() != _make_session_id()


class TestPlayerId:
    def test_construction(self) -> None:
        uid = uuid4()
        pid = PlayerId(value=uid)
        assert pid.value == uid

    def test_immutability(self) -> None:
        pid = _make_player_id()
        with pytest.raises(AttributeError):
            pid.value = uuid4()  # type: ignore[misc]

    def test_equality(self) -> None:
        uid = uuid4()
        assert PlayerId(value=uid) == PlayerId(value=uid)

    def test_inequality(self) -> None:
        assert _make_player_id() != _make_player_id()


class TestGameInput:
    def test_construction(self) -> None:
        gi = _make_game_input()
        assert gi.button == Button.A
        assert gi.timestamp == datetime(2026, 1, 1, 12, 0, 0)
        assert isinstance(gi.player_id, PlayerId)

    def test_immutability(self) -> None:
        gi = _make_game_input()
        with pytest.raises(AttributeError):
            gi.button = Button.B  # type: ignore[misc]

    def test_equality(self) -> None:
        pid = _make_player_id()
        ts = datetime(2026, 1, 1, 12, 0, 0)
        assert GameInput(button=Button.LEFT, timestamp=ts, player_id=pid) == GameInput(
            button=Button.LEFT, timestamp=ts, player_id=pid
        )

    def test_inequality(self) -> None:
        assert _make_game_input(button=Button.A) != _make_game_input(button=Button.B)


class TestSessionConfiguration:
    def test_construction(self) -> None:
        sc = SessionConfiguration(
            control_mode=ControlMode.FIFO,
            voting_interval=timedelta(seconds=1),
            autosave_interval=timedelta(seconds=15),
        )
        assert sc.control_mode == ControlMode.FIFO
        assert sc.voting_interval == timedelta(seconds=1)
        assert sc.autosave_interval == timedelta(seconds=15)

    def test_immutability(self) -> None:
        sc = SessionConfiguration(
            control_mode=ControlMode.FIFO,
            voting_interval=timedelta(seconds=1),
            autosave_interval=timedelta(seconds=15),
        )
        with pytest.raises(AttributeError):
            sc.control_mode = ControlMode.VOTING  # type: ignore[misc]

    def test_equality(self) -> None:
        kwargs = {
            "control_mode": ControlMode.VOTING,
            "voting_interval": timedelta(seconds=2),
            "autosave_interval": timedelta(seconds=30),
        }
        assert SessionConfiguration(**kwargs) == SessionConfiguration(**kwargs)  # type: ignore[arg-type]


class TestSaveMetadata:
    def test_construction(self) -> None:
        ts = datetime(2026, 1, 1, 12, 0, 0)
        sm = SaveMetadata(last_save_at=ts, save_count=5)
        assert sm.last_save_at == ts
        assert sm.save_count == 5

    def test_immutability(self) -> None:
        sm = SaveMetadata(last_save_at=datetime.now(), save_count=1)
        with pytest.raises(AttributeError):
            sm.save_count = 2  # type: ignore[misc]

    def test_equality(self) -> None:
        ts = datetime(2026, 1, 1, 12, 0, 0)
        assert SaveMetadata(last_save_at=ts, save_count=3) == SaveMetadata(
            last_save_at=ts, save_count=3
        )


class TestPlayerStatistics:
    def test_construction(self) -> None:
        ps = PlayerStatistics(
            submitted_commands=10,
            winning_votes=3,
            connected_duration=timedelta(minutes=5),
        )
        assert ps.submitted_commands == 10
        assert ps.winning_votes == 3
        assert ps.connected_duration == timedelta(minutes=5)

    def test_immutability(self) -> None:
        ps = PlayerStatistics(
            submitted_commands=0,
            winning_votes=0,
            connected_duration=timedelta(),
        )
        with pytest.raises(AttributeError):
            ps.submitted_commands = 1  # type: ignore[misc]

    def test_equality(self) -> None:
        kwargs = {
            "submitted_commands": 5,
            "winning_votes": 2,
            "connected_duration": timedelta(minutes=10),
        }
        assert PlayerStatistics(**kwargs) == PlayerStatistics(**kwargs)  # type: ignore[arg-type]


class TestVoteResult:
    def test_construction(self) -> None:
        gi = _make_game_input()
        vr = VoteResult(winning_input=gi, vote_count=7)
        assert vr.winning_input == gi
        assert vr.vote_count == 7

    def test_immutability(self) -> None:
        vr = VoteResult(winning_input=_make_game_input(), vote_count=1)
        with pytest.raises(AttributeError):
            vr.vote_count = 2  # type: ignore[misc]

    def test_equality(self) -> None:
        gi = _make_game_input()
        assert VoteResult(winning_input=gi, vote_count=5) == VoteResult(
            winning_input=gi, vote_count=5
        )

    def test_inequality(self) -> None:
        gi = _make_game_input()
        assert VoteResult(winning_input=gi, vote_count=1) != VoteResult(
            winning_input=gi, vote_count=2
        )
