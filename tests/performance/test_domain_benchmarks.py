from __future__ import annotations

from datetime import datetime
from uuid import uuid4

from consumer.domain.composed.input_queue import InputQueue
from consumer.domain.composed.session_state_machine import SessionStateMachine
from consumer.domain.composed.vote_round import VoteRound
from consumer.domain.enums import Button, SessionState
from consumer.domain.services.vote_resolver import VoteResolver
from consumer.domain.value_objects import GameInput, PlayerId


def test_input_queue_enqueue(benchmark: object) -> None:
    gi = GameInput(
        button=Button.A,
        timestamp=datetime(2026, 1, 1, 12, 0, 0),
        player_id=PlayerId(value=uuid4()),
    )

    def _run() -> None:
        q = InputQueue()
        q.enqueue(gi)

    benchmark(_run)  # type: ignore[operator]


def test_input_queue_dequeue(benchmark: object) -> None:
    dequeue_item: object

    def _run() -> None:
        q = InputQueue()
        gi = GameInput(
            button=Button.A,
            timestamp=datetime(2026, 1, 1, 12, 0, 0),
            player_id=PlayerId(value=uuid4()),
        )
        q.enqueue(gi)
        nonlocal dequeue_item
        dequeue_item = q.dequeue()

    benchmark(_run)  # type: ignore[operator]


def test_state_machine_transition(benchmark: object) -> None:
    def _run() -> None:
        sm = SessionStateMachine()
        sm.transition_to(SessionState.RUNNING)

    benchmark(_run)  # type: ignore[operator]


def test_game_input_creation(benchmark: object) -> None:
    def _run() -> GameInput:
        return GameInput(
            button=Button.A,
            timestamp=datetime(2026, 1, 1, 12, 0, 0),
            player_id=PlayerId(value=uuid4()),
        )

    benchmark(_run)  # type: ignore[operator]


def test_vote_resolver(benchmark: object) -> None:
    def _run() -> None:
        round_ = VoteRound()
        pid1 = PlayerId(value=uuid4())
        pid2 = PlayerId(value=uuid4())
        pid3 = PlayerId(value=uuid4())
        round_.collect_vote(
            pid1,
            GameInput(
                button=Button.A,
                timestamp=datetime(2026, 1, 1, 12, 0, 0),
                player_id=pid1,
            ),
        )
        round_.collect_vote(
            pid2,
            GameInput(
                button=Button.A,
                timestamp=datetime(2026, 1, 1, 12, 0, 1),
                player_id=pid2,
            ),
        )
        round_.collect_vote(
            pid3,
            GameInput(
                button=Button.B,
                timestamp=datetime(2026, 1, 1, 12, 0, 2),
                player_id=pid3,
            ),
        )
        VoteResolver.resolve(round_)

    benchmark(_run)  # type: ignore[operator]
