from datetime import datetime
from uuid import uuid4

import pytest

from consumer.domain.composed.input_queue import InputQueue
from consumer.domain.enums import Button
from consumer.domain.value_objects import GameInput, PlayerId


def _make_game_input(button: Button = Button.A) -> GameInput:
    return GameInput(
        button=button,
        timestamp=datetime(2026, 1, 1, 12, 0, 0),
        player_id=PlayerId(value=uuid4()),
    )


class TestInputQueue:
    def test_initial_size_is_zero(self) -> None:
        assert InputQueue().size == 0

    def test_enqueue_increases_size(self) -> None:
        q = InputQueue()
        q.enqueue(_make_game_input())
        assert q.size == 1

    def test_enqueue_multiple(self) -> None:
        q = InputQueue()
        q.enqueue(_make_game_input(Button.A))
        q.enqueue(_make_game_input(Button.B))
        assert q.size == 2

    def test_dequeue_returns_first_item(self) -> None:
        q = InputQueue()
        first = _make_game_input(Button.LEFT)
        second = _make_game_input(Button.RIGHT)
        q.enqueue(first)
        q.enqueue(second)
        assert q.dequeue() is first
        assert q.dequeue() is second

    def test_dequeue_decreases_size(self) -> None:
        q = InputQueue()
        q.enqueue(_make_game_input())
        q.dequeue()
        assert q.size == 0

    def test_dequeue_from_empty_raises(self) -> None:
        with pytest.raises(IndexError, match="empty"):
            InputQueue().dequeue()

    def test_peek_returns_first_item(self) -> None:
        q = InputQueue()
        first = _make_game_input(Button.A)
        q.enqueue(first)
        q.enqueue(_make_game_input(Button.B))
        assert q.peek() is first

    def test_peek_does_not_remove(self) -> None:
        q = InputQueue()
        q.enqueue(_make_game_input())
        q.peek()
        assert q.size == 1

    def test_peek_from_empty_raises(self) -> None:
        with pytest.raises(IndexError, match="empty"):
            InputQueue().peek()

    def test_clear_removes_all(self) -> None:
        q = InputQueue()
        q.enqueue(_make_game_input())
        q.enqueue(_make_game_input())
        q.clear()
        assert q.size == 0

    def test_clear_on_empty_is_noop(self) -> None:
        q = InputQueue()
        q.clear()
        assert q.size == 0
