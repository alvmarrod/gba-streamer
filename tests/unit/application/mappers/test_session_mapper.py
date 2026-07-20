from datetime import timedelta
from uuid import uuid4

from consumer.application.dto.session import StartSessionRequest
from consumer.application.mappers.session_mapper import SessionMapper
from consumer.domain.enums import ControlMode, SessionState


class TestSessionMapper:
    def test_to_session_config(self) -> None:
        req = StartSessionRequest(
            control_mode=ControlMode.VOTING,
            voting_interval=timedelta(seconds=30),
            autosave_interval=timedelta(minutes=5),
        )
        config = SessionMapper.to_session_config(req)

        assert config.control_mode == ControlMode.VOTING
        assert config.voting_interval == timedelta(seconds=30)
        assert config.autosave_interval == timedelta(minutes=5)

    def test_to_start_response(self) -> None:
        sid = uuid4()
        resp = SessionMapper.to_start_response(sid, SessionState.RUNNING)

        assert resp.session_id == sid
        assert resp.state == SessionState.RUNNING

    def test_to_stop_response(self) -> None:
        resp = SessionMapper.to_stop_response(SessionState.STOPPING)
        assert resp.state == SessionState.STOPPING

    def test_to_pause_response(self) -> None:
        resp = SessionMapper.to_pause_response(SessionState.PAUSED)
        assert resp.state == SessionState.PAUSED

    def test_to_resume_response(self) -> None:
        resp = SessionMapper.to_resume_response(SessionState.RUNNING)
        assert resp.state == SessionState.RUNNING

    def test_to_restore_response(self) -> None:
        sid = uuid4()
        resp = SessionMapper.to_restore_response(sid, SessionState.RUNNING)

        assert resp.session_id == sid
        assert resp.state == SessionState.RUNNING
