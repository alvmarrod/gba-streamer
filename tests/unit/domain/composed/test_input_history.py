from datetime import datetime, timezone
from uuid import uuid4

from consumer.domain.composed.input_history import InputHistory
from consumer.domain.enums import Button
from consumer.domain.value_objects import GameInput, PlayerId


def _make_game_input(button: Button = Button.A) -> GameInput:
    return GameInput(
        button=button,
        timestamp=datetime.now(tz=timezone.utc),
        player_id=PlayerId(value=uuid4()),
    )


class TestInputHistory:
    def test_initial_entries_are_empty(self) -> None:
        history = InputHistory()
        assert history.entries == []

    def test_record_adds_entry(self) -> None:
        history = InputHistory()
        gi = _make_game_input(Button.LEFT)
        history.record(gi)
        assert len(history.entries) == 1
        assert history.entries[0] is gi

    def test_record_multiple(self) -> None:
        history = InputHistory()
        first = _make_game_input(Button.A)
        second = _make_game_input(Button.B)
        history.record(first)
        history.record(second)
        assert history.entries == [first, second]

    def test_capped_at_five(self) -> None:
        history = InputHistory()
        buttons = [
            _make_game_input(button)
            for button in (
                Button.A,
                Button.B,
                Button.UP,
                Button.DOWN,
                Button.LEFT,
                Button.RIGHT,
            )
        ]
        for gi in buttons:
            history.record(gi)
        assert len(history.entries) == 5
        assert history.entries[0] is buttons[1]  # B — A was evicted
        assert history.entries[-1] is buttons[-1]  # RIGHT
