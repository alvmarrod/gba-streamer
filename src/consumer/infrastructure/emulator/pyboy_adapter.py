from __future__ import annotations

import asyncio
import io
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from pyboy import PyBoy  # type: ignore[import-untyped]

from consumer.application.ports.emulator_control_port import EmulatorControlPort
from consumer.application.ports.framebuffer_provider_port import (
    FramebufferProviderPort,
)
from consumer.application.ports.snapshot_port import SnapshotPort
from consumer.domain.enums import Button
from consumer.domain.value_objects import GameInput

_BUTTON_MAP: dict[Button, str] = {
    Button.UP: "up",
    Button.DOWN: "down",
    Button.LEFT: "left",
    Button.RIGHT: "right",
    Button.A: "a",
    Button.B: "b",
    Button.START: "start",
    Button.SELECT: "select",
}


class PyBoyAdapter(EmulatorControlPort, SnapshotPort, FramebufferProviderPort):
    def __init__(self, rom_path: str | Path) -> None:
        self._pyboy = PyBoy(str(rom_path), window="null")
        self._pending_inputs: list[str] = []
        self._executor = ThreadPoolExecutor(max_workers=1)

    async def execute_input(self, game_input: GameInput) -> None:
        self._pending_inputs.append(_BUTTON_MAP[game_input.button])

    async def tick(self) -> None:
        await asyncio.get_event_loop().run_in_executor(self._executor, self._tick_sync)

    async def get_framebuffer(self) -> bytes:
        return await asyncio.get_event_loop().run_in_executor(
            self._executor, self._get_framebuffer_sync
        )

    async def create_snapshot(self) -> bytes:
        return await asyncio.get_event_loop().run_in_executor(
            self._executor, self._create_snapshot_sync
        )

    async def restore_snapshot(self, data: bytes) -> None:
        await asyncio.get_event_loop().run_in_executor(
            self._executor, self._restore_snapshot_sync, data
        )

    def _tick_sync(self) -> None:
        for button_str in self._pending_inputs:
            self._pyboy.button(button_str)
        self._pending_inputs.clear()
        self._pyboy.tick()

    def _get_framebuffer_sync(self) -> bytes:
        return bytes(self._pyboy.screen.raw_buffer)

    def _create_snapshot_sync(self) -> bytes:
        buf = io.BytesIO()
        self._pyboy.save_state(buf)
        return buf.getvalue()

    def _restore_snapshot_sync(self, data: bytes) -> None:
        self._pyboy.load_state(io.BytesIO(data))
