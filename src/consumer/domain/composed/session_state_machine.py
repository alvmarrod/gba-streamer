from __future__ import annotations

from consumer.domain.composed.exceptions import InvalidSessionStateException
from consumer.domain.enums import SessionState


_VALID_TRANSITIONS: dict[SessionState, set[SessionState]] = {
    SessionState.STARTING: {SessionState.RUNNING},
    SessionState.RUNNING: {SessionState.PAUSED, SessionState.STOPPING},
    SessionState.PAUSED: {SessionState.RUNNING},
    SessionState.STOPPING: {SessionState.STOPPED},
    SessionState.STOPPED: set(),
}


class SessionStateMachine:
    def __init__(self, initial_state: SessionState = SessionState.STARTING) -> None:
        self._current_state: SessionState = initial_state

    @property
    def current_state(self) -> SessionState:
        return self._current_state

    def transition_to(self, new_state: SessionState) -> None:
        allowed = _VALID_TRANSITIONS.get(self._current_state, set())
        if new_state not in allowed:
            raise InvalidSessionStateException(
                f"Invalid transition: {self._current_state.value} → {new_state.value}"
            )
        self._current_state = new_state
