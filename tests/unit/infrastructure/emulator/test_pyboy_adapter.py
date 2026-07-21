from __future__ import annotations

import io
from concurrent.futures import ThreadPoolExecutor
from unittest.mock import MagicMock


from consumer.domain.enums import Button
from consumer.domain.value_objects import GameInput, PlayerId
from consumer.infrastructure.emulator.pyboy_adapter import (
    PyBoyAdapter,
    _BUTTON_MAP,
)
from datetime import datetime, timezone


class TestButtonMap:
    def test_all_buttons_mapped(self) -> None:
        for button in Button:
            assert button in _BUTTON_MAP
            assert isinstance(_BUTTON_MAP[button], str)

    def test_button_names_lowercase(self) -> None:
        for _button, name in _BUTTON_MAP.items():
            assert name == name.lower()
            assert name.isalpha()

    def test_expected_button_names(self) -> None:
        expected = {
            Button.UP: "up",
            Button.DOWN: "down",
            Button.LEFT: "left",
            Button.RIGHT: "right",
            Button.A: "a",
            Button.B: "b",
            Button.START: "start",
            Button.SELECT: "select",
        }
        assert _BUTTON_MAP == expected


def _make_game_input(button: Button) -> GameInput:
    return GameInput(
        button=button,
        timestamp=datetime.now(tz=timezone.utc),
        player_id=PlayerId(value=__import__("uuid").uuid4()),
    )


def _mock_pyboy() -> MagicMock:
    mock = MagicMock()
    mock.screen.raw_buffer = memoryview(b"\x00" * 92160)
    return mock


def _make_adapter(mock_pyboy: MagicMock) -> PyBoyAdapter:
    adapter = PyBoyAdapter.__new__(PyBoyAdapter)
    adapter._pyboy = mock_pyboy
    adapter._pending_inputs = []
    adapter._executor = ThreadPoolExecutor(max_workers=1)
    return adapter


class TestPyBoyAdapterExecuteInput:
    async def test_queues_button_string(self) -> None:
        adapter = _make_adapter(_mock_pyboy())
        await adapter.execute_input(_make_game_input(Button.A))
        assert adapter._pending_inputs == ["a"]

    async def test_queues_multiple_inputs(self) -> None:
        adapter = _make_adapter(_mock_pyboy())
        for button in [Button.UP, Button.A, Button.LEFT]:
            await adapter.execute_input(_make_game_input(button))
        assert adapter._pending_inputs == ["up", "a", "left"]


class TestPyBoyAdapterTick:
    async def test_applies_all_buttons_then_one_tick(self) -> None:
        mock_pyboy = _mock_pyboy()
        adapter = _make_adapter(mock_pyboy)
        adapter._pending_inputs = ["a", "b"]

        await adapter.tick()

        calls = [str(c) for c in mock_pyboy.method_calls]
        button_calls = [c for c in calls if "button" in c]
        tick_calls = [c for c in calls if "tick" in c]

        assert len(button_calls) == 2
        assert len(tick_calls) == 1

    async def test_clears_pending_after_tick(self) -> None:
        adapter = _make_adapter(_mock_pyboy())
        adapter._pending_inputs = ["up"]

        await adapter.tick()

        assert adapter._pending_inputs == []

    async def test_empty_pending_still_ticks(self) -> None:
        mock_pyboy = _mock_pyboy()
        adapter = _make_adapter(mock_pyboy)

        await adapter.tick()

        mock_pyboy.tick.assert_called()


class TestPyBoyAdapterFramebuffer:
    async def test_returns_raw_buffer_as_bytes(self) -> None:
        mock_pyboy = _mock_pyboy()
        mock_pyboy.screen.raw_buffer = memoryview(b"\xff" * 100)
        adapter = _make_adapter(mock_pyboy)

        result = await adapter.get_framebuffer()

        assert isinstance(result, bytes)
        assert result == b"\xff" * 100


class TestPyBoyAdapterSnapshot:
    async def test_create_snapshot_returns_bytes(self) -> None:
        mock_pyboy = _mock_pyboy()

        def fake_save_state(f: io.BufferedIOBase) -> None:
            f.write(b"snapshot-data")

        mock_pyboy.save_state.side_effect = fake_save_state
        adapter = _make_adapter(mock_pyboy)

        result = await adapter.create_snapshot()

        assert result == b"snapshot-data"

    async def test_restore_snapshot_passes_bytes_to_load_state(self) -> None:
        mock_pyboy = _mock_pyboy()
        adapter = _make_adapter(mock_pyboy)

        await adapter.restore_snapshot(b"restore-data")

        mock_pyboy.load_state.assert_called_once()
        buf = mock_pyboy.load_state.call_args[0][0]
        assert isinstance(buf, io.BytesIO)
        assert buf.getvalue() == b"restore-data"
