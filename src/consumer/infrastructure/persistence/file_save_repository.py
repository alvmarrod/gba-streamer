from __future__ import annotations

import asyncio
from pathlib import Path

from consumer.application.ports.save_repository_port import SaveRepositoryPort

_SAVE_FILENAME = "game_state.sav"


class FileSaveRepository(SaveRepositoryPort):
    def __init__(self, save_dir: Path) -> None:
        self._save_dir = save_dir

    async def save(self, data: bytes) -> None:
        await asyncio.to_thread(self._save_sync, data)

    async def load(self) -> bytes:
        return await asyncio.to_thread(self._load_sync)

    def _save_sync(self, data: bytes) -> None:
        self._save_dir.mkdir(parents=True, exist_ok=True)
        target = self._save_dir / _SAVE_FILENAME
        tmp = target.with_suffix(".tmp")
        tmp.write_bytes(data)
        tmp.rename(target)

    def _load_sync(self) -> bytes:
        target = self._save_dir / _SAVE_FILENAME
        if not target.exists():
            raise FileNotFoundError(f"Save file not found: {target}")
        return target.read_bytes()
