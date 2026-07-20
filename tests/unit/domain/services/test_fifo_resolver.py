from datetime import datetime, timezone
from uuid import uuid4

import pytest

from consumer.domain.composed.input_queue import InputQueue
from consumer.domain.enums import Button
from consumer.domain.services.fifo_resolver import FIFOResolver
from consumer.domain.value_objects import GameInput, PlayerId


class TestFIFOResolver:
    def test_resolve_single_item(self) -> None:
        queue = InputQueue()
        player_id = PlayerId(uuid4())
        game_input = GameInput(
            button=Button.A,
            timestamp=datetime.now(tz=timezone.utc),
            player_id=player_id,
        )
        queue.enqueue(game_input)

        result = FIFOResolver.resolve(queue)

        assert result is game_input
        assert queue.size == 0

    def test_resolve_fifo_order(self) -> None:
        queue = InputQueue()
        player_id = PlayerId(uuid4())
        now = datetime.now(tz=timezone.utc)
        first = GameInput(button=Button.UP, timestamp=now, player_id=player_id)
        second = GameInput(button=Button.DOWN, timestamp=now, player_id=player_id)
        third = GameInput(button=Button.A, timestamp=now, player_id=player_id)

        queue.enqueue(first)
        queue.enqueue(second)
        queue.enqueue(third)

        assert FIFOResolver.resolve(queue) is first
        assert FIFOResolver.resolve(queue) is second
        assert FIFOResolver.resolve(queue) is third

    def test_resolve_empty_queue_raises(self) -> None:
        queue = InputQueue()
        with pytest.raises(IndexError):
            FIFOResolver.resolve(queue)
