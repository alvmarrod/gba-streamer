from __future__ import annotations

import asyncio
import json
from pathlib import Path
from typing import Any

from consumer.application.ports.save_repository_port import SaveRepositoryPort

_SAVE_FILENAME = "game_state.sav"
_METADATA_FILENAME = "save_metadata.json"


class FileSaveRepository(SaveRepositoryPort):
    def __init__(self, save_dir: Path) -> None:
        self._save_dir = save_dir

    async def save(self, data: bytes) -> None:
        await asyncio.to_thread(self._save_sync, data)

    async def load(self) -> bytes:
        return await asyncio.to_thread(self._load_sync)

    async def save_metadata(self, metadata: dict[str, Any]) -> None:
        await asyncio.to_thread(self._save_metadata_sync, metadata)

    async def load_metadata(self) -> dict[str, Any]:
        return await asyncio.to_thread(self._load_metadata_sync)

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

    def _save_metadata_sync(self, metadata: dict[str, Any]) -> None:
        self._save_dir.mkdir(parents=True, exist_ok=True)
        target = self._save_dir / _METADATA_FILENAME
        tmp = target.with_suffix(".tmp")
        tmp.write_text(json.dumps(metadata, default=str))
        tmp.rename(target)

    def _load_metadata_sync(self) -> dict[str, Any]:
        target = self._save_dir / _METADATA_FILENAME
        if not target.exists():
            raise FileNotFoundError(f"Metadata file not found: {target}")
        return json.loads(target.read_text())  # type: ignore[no-any-return]
