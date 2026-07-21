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

    def test_running_to_stopped(self) -> None:
        sm = SessionStateMachine(initial_state=SessionState.RUNNING)
        sm.transition_to(SessionState.STOPPED)
        assert sm.current_state == SessionState.STOPPED

    def test_stopped_to_starting(self) -> None:
        sm = SessionStateMachine(initial_state=SessionState.STOPPED)
        sm.transition_to(SessionState.STARTING)
        assert sm.current_state == SessionState.STARTING

    def test_full_lifecycle(self) -> None:
        sm = SessionStateMachine()
        sm.transition_to(SessionState.RUNNING)
        sm.transition_to(SessionState.PAUSED)
        sm.transition_to(SessionState.RUNNING)
        sm.transition_to(SessionState.STOPPED)
        sm.transition_to(SessionState.STARTING)
        sm.transition_to(SessionState.RUNNING)
        assert sm.current_state == SessionState.RUNNING

    def test_starting_to_paused_invalid(self) -> None:
        sm = SessionStateMachine()
        with pytest.raises(InvalidSessionStateException):
            sm.transition_to(SessionState.PAUSED)

    def test_starting_to_stopped_invalid(self) -> None:
        sm = SessionStateMachine()
        with pytest.raises(InvalidSessionStateException):
            sm.transition_to(SessionState.STOPPED)

    def test_stopped_to_paused_invalid(self) -> None:
        sm = SessionStateMachine(initial_state=SessionState.STOPPED)
        with pytest.raises(InvalidSessionStateException):
            sm.transition_to(SessionState.PAUSED)

    def test_paused_to_stopped_invalid(self) -> None:
        sm = SessionStateMachine(initial_state=SessionState.PAUSED)
        with pytest.raises(InvalidSessionStateException):
            sm.transition_to(SessionState.STOPPED)
