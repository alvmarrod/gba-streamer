from datetime import timedelta
from uuid import uuid4

import pytest

from consumer.application.dto.session import (
    PauseSessionRequest,
    PauseSessionResponse,
    ResumeSessionRequest,
    ResumeSessionResponse,
    RestoreSessionRequest,
    RestoreSessionResponse,
    StartSessionRequest,
    StartSessionResponse,
    StopSessionRequest,
    StopSessionResponse,
)
from consumer.domain.enums import ControlMode, SessionState


class TestStartSessionDTOs:
    def test_request_construction(self) -> None:
        req = StartSessionRequest(
            control_mode=ControlMode.FIFO,
            voting_interval=timedelta(seconds=30),
            autosave_interval=timedelta(minutes=5),
        )
        assert req.control_mode == ControlMode.FIFO
        assert req.voting_interval == timedelta(seconds=30)
        assert req.autosave_interval == timedelta(minutes=5)

    def test_request_immutability(self) -> None:
        req = StartSessionRequest(
            control_mode=ControlMode.FIFO,
            voting_interval=timedelta(seconds=30),
            autosave_interval=timedelta(minutes=5),
        )
        with pytest.raises(AttributeError):
            req.control_mode = ControlMode.VOTING  # type: ignore[misc]

    def test_response_construction(self) -> None:
        sid = uuid4()
        resp = StartSessionResponse(session_id=sid, state=SessionState.RUNNING)
        assert resp.session_id == sid
        assert resp.state == SessionState.RUNNING

    def test_response_immutability(self) -> None:
        resp = StartSessionResponse(session_id=uuid4(), state=SessionState.RUNNING)
        with pytest.raises(AttributeError):
            resp.state = SessionState.STOPPED  # type: ignore[misc]


class TestStopSessionDTOs:
    def test_request_construction(self) -> None:
        req = StopSessionRequest()
        assert req is not None

    def test_response_construction(self) -> None:
        resp = StopSessionResponse(state=SessionState.STOPPED)
        assert resp.state == SessionState.STOPPED


class TestPauseSessionDTOs:
    def test_request_construction(self) -> None:
        req = PauseSessionRequest()
        assert req is not None

    def test_response_construction(self) -> None:
        resp = PauseSessionResponse(state=SessionState.PAUSED)
        assert resp.state == SessionState.PAUSED


class TestResumeSessionDTOs:
    def test_request_construction(self) -> None:
        req = ResumeSessionRequest()
        assert req is not None

    def test_response_construction(self) -> None:
        resp = ResumeSessionResponse(state=SessionState.RUNNING)
        assert resp.state == SessionState.RUNNING


class TestRestoreSessionDTOs:
    def test_request_construction(self) -> None:
        req = RestoreSessionRequest(save_path="/saves/game.sav")
        assert req.save_path == "/saves/game.sav"

    def test_request_immutability(self) -> None:
        req = RestoreSessionRequest(save_path="/saves/game.sav")
        with pytest.raises(AttributeError):
            req.save_path = "/other"  # type: ignore[misc]

    def test_response_construction(self) -> None:
        sid = uuid4()
        resp = RestoreSessionResponse(session_id=sid, state=SessionState.RUNNING)
        assert resp.session_id == sid
        assert resp.state == SessionState.RUNNING
