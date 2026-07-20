from __future__ import annotations

from uuid import UUID

from consumer.domain.enums import SessionState
from consumer.domain.value_objects import SessionConfiguration

from consumer.application.dto.session import (
    PauseSessionResponse,
    ResumeSessionResponse,
    RestoreSessionResponse,
    StartSessionRequest,
    StartSessionResponse,
    StopSessionResponse,
)


class SessionMapper:
    @staticmethod
    def to_session_config(request: StartSessionRequest) -> SessionConfiguration:
        return SessionConfiguration(
            control_mode=request.control_mode,
            voting_interval=request.voting_interval,
            autosave_interval=request.autosave_interval,
        )

    @staticmethod
    def to_start_response(
        session_id: UUID, state: SessionState
    ) -> StartSessionResponse:
        return StartSessionResponse(session_id=session_id, state=state)

    @staticmethod
    def to_stop_response(state: SessionState) -> StopSessionResponse:
        return StopSessionResponse(state=state)

    @staticmethod
    def to_pause_response(state: SessionState) -> PauseSessionResponse:
        return PauseSessionResponse(state=state)

    @staticmethod
    def to_resume_response(state: SessionState) -> ResumeSessionResponse:
        return ResumeSessionResponse(state=state)

    @staticmethod
    def to_restore_response(
        session_id: UUID, state: SessionState
    ) -> RestoreSessionResponse:
        return RestoreSessionResponse(session_id=session_id, state=state)
