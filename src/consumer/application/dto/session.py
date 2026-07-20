from dataclasses import dataclass
from datetime import timedelta
from uuid import UUID

from consumer.domain.enums import ControlMode, SessionState


@dataclass(frozen=True)
class StartSessionRequest:
    control_mode: ControlMode
    voting_interval: timedelta
    autosave_interval: timedelta


@dataclass(frozen=True)
class StartSessionResponse:
    session_id: UUID
    state: SessionState


@dataclass(frozen=True)
class StopSessionRequest:
    pass


@dataclass(frozen=True)
class StopSessionResponse:
    state: SessionState


@dataclass(frozen=True)
class PauseSessionRequest:
    pass


@dataclass(frozen=True)
class PauseSessionResponse:
    state: SessionState


@dataclass(frozen=True)
class ResumeSessionRequest:
    pass


@dataclass(frozen=True)
class ResumeSessionResponse:
    state: SessionState


@dataclass(frozen=True)
class RestoreSessionRequest:
    save_path: str


@dataclass(frozen=True)
class RestoreSessionResponse:
    session_id: UUID
    state: SessionState
