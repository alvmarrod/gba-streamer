import pytest

from consumer.domain.composed.exceptions import InvalidSessionStateException
from consumer.domain.composed.session_state_machine import SessionStateMachine
from consumer.domain.enums import SessionState


class TestSessionStateMachine:
    def test_initial_state(self) -> None:
        sm = SessionStateMachine()
        assert sm.current_state == SessionState.STARTING

    def test_custom_initial_state(self) -> None:
        sm = SessionStateMachine(initial_state=SessionState.RUNNING)
        assert sm.current_state == SessionState.RUNNING

    def test_starting_to_running(self) -> None:
        sm = SessionStateMachine()
        sm.transition_to(SessionState.RUNNING)
        assert sm.current_state == SessionState.RUNNING

    def test_running_to_paused(self) -> None:
        sm = SessionStateMachine(initial_state=SessionState.RUNNING)
        sm.transition_to(SessionState.PAUSED)
        assert sm.current_state == SessionState.PAUSED

    def test_paused_to_running(self) -> None:
        sm = SessionStateMachine(initial_state=SessionState.PAUSED)
        sm.transition_to(SessionState.RUNNING)
        assert sm.current_state == SessionState.RUNNING

    def test_running_to_stopping(self) -> None:
        sm = SessionStateMachine(initial_state=SessionState.RUNNING)
        sm.transition_to(SessionState.STOPPING)
        assert sm.current_state == SessionState.STOPPING

    def test_stopping_to_stopped(self) -> None:
        sm = SessionStateMachine(initial_state=SessionState.STOPPING)
        sm.transition_to(SessionState.STOPPED)
        assert sm.current_state == SessionState.STOPPED

    def test_full_lifecycle(self) -> None:
        sm = SessionStateMachine()
        sm.transition_to(SessionState.RUNNING)
        sm.transition_to(SessionState.PAUSED)
        sm.transition_to(SessionState.RUNNING)
        sm.transition_to(SessionState.STOPPING)
        sm.transition_to(SessionState.STOPPED)
        assert sm.current_state == SessionState.STOPPED

    def test_starting_to_paused_invalid(self) -> None:
        sm = SessionStateMachine()
        with pytest.raises(InvalidSessionStateException):
            sm.transition_to(SessionState.PAUSED)

    def test_starting_to_stopping_invalid(self) -> None:
        sm = SessionStateMachine()
        with pytest.raises(InvalidSessionStateException):
            sm.transition_to(SessionState.STOPPING)

    def test_stopped_to_any_invalid(self) -> None:
        sm = SessionStateMachine(initial_state=SessionState.STOPPED)
        for target in [
            SessionState.STARTING,
            SessionState.RUNNING,
            SessionState.PAUSED,
            SessionState.STOPPING,
        ]:
            with pytest.raises(InvalidSessionStateException):
                sm.transition_to(target)

    def test_paused_to_stopping_invalid(self) -> None:
        sm = SessionStateMachine(initial_state=SessionState.PAUSED)
        with pytest.raises(InvalidSessionStateException):
            sm.transition_to(SessionState.STOPPING)
