from __future__ import annotations

from pathlib import Path

import pytest

from consumer.infrastructure.persistence.file_save_repository import (
    FileSaveRepository,
)

_SAVE_FILENAME = "game_state.sav"


class TestFileSaveRepository:
    async def test_save_creates_file(self, tmp_path: Path) -> None:
        repo = FileSaveRepository(tmp_path)
        await repo.save(b"hello")

        assert (tmp_path / _SAVE_FILENAME).exists()

    async def test_load_roundtrip(self, tmp_path: Path) -> None:
        repo = FileSaveRepository(tmp_path)
        await repo.save(b"roundtrip-data")

        result = await repo.load()
        assert result == b"roundtrip-data"

    async def test_load_missing_raises(self, tmp_path: Path) -> None:
        repo = FileSaveRepository(tmp_path / "nonexistent")

        with pytest.raises(FileNotFoundError):
            await repo.load()

    async def test_no_tmp_leftover(self, tmp_path: Path) -> None:
        repo = FileSaveRepository(tmp_path)
        await repo.save(b"atomic")

        tmp_files = list(tmp_path.glob("*.tmp"))
        assert len(tmp_files) == 0

    async def test_save_overwrites(self, tmp_path: Path) -> None:
        repo = FileSaveRepository(tmp_path)
        await repo.save(b"first")
        await repo.save(b"second")

        result = await repo.load()
        assert result == b"second"

    async def test_save_creates_parent_dirs(self, tmp_path: Path) -> None:
        repo = FileSaveRepository(tmp_path / "nested" / "deep")
        await repo.save(b"nested")

        assert (tmp_path / "nested" / "deep" / _SAVE_FILENAME).exists()
