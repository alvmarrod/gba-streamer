from __future__ import annotations

from pathlib import Path

import pytest

from consumer.domain.enums import Button
from consumer.domain.value_objects import GameInput, PlayerId
from consumer.infrastructure.emulator.pyboy_adapter import PyBoyAdapter
from datetime import datetime, timezone
from uuid import uuid4


@pytest.fixture
def adapter(rom_path: Path) -> PyBoyAdapter:
    return PyBoyAdapter(rom_path)


def _input(button: Button) -> GameInput:
    return GameInput(
        button=button,
        timestamp=datetime.now(tz=timezone.utc),
        player_id=PlayerId(value=uuid4()),
    )


class TestPyBoyAdapterInit:
    async def test_adapter_initializes_with_rom(self, adapter: PyBoyAdapter) -> None:
        assert adapter._pyboy is not None


class TestPyBoyAdapterTick:
    async def test_tick_advances_emulator(self, adapter: PyBoyAdapter) -> None:
        for _ in range(10):
            await adapter.tick()

    async def test_multiple_inputs_per_tick(self, adapter: PyBoyAdapter) -> None:
        await adapter.execute_input(_input(Button.UP))
        await adapter.execute_input(_input(Button.A))
        await adapter.execute_input(_input(Button.LEFT))
        await adapter.tick()
        assert adapter._pending_inputs == []


class TestPyBoyAdapterFramebuffer:
    async def test_get_framebuffer_returns_correct_size(
        self, adapter: PyBoyAdapter
    ) -> None:
        await adapter.tick()
        fb = await adapter.get_framebuffer()
        assert isinstance(fb, bytes)
        assert len(fb) == 160 * 144 * 4

    async def test_framebuffer_changes_over_time(self, adapter: PyBoyAdapter) -> None:
        await adapter.tick()
        fb1 = await adapter.get_framebuffer()
        for _ in range(30):
            await adapter.tick()
        fb2 = await adapter.get_framebuffer()
        assert fb1 != fb2


class TestPyBoyAdapterSnapshot:
    async def test_create_snapshot_returns_nonempty_bytes(
        self, adapter: PyBoyAdapter
    ) -> None:
        await adapter.tick()
        snap = await adapter.create_snapshot()
        assert isinstance(snap, bytes)
        assert len(snap) > 0

    async def test_snapshot_round_trip(self, adapter: PyBoyAdapter) -> None:
        await adapter.tick()
        snap_before = await adapter.create_snapshot()

        await adapter.execute_input(_input(Button.A))
        await adapter.tick()
        await adapter.execute_input(_input(Button.B))
        await adapter.tick()

        await adapter.restore_snapshot(snap_before)
        snap_after = await adapter.create_snapshot()

        assert snap_before == snap_after
