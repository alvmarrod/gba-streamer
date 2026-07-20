from __future__ import annotations

from pathlib import Path

import pytest

from consumer.infrastructure.persistence.file_save_repository import (
    FileSaveRepository,
)


class TestFileSaveRepositorySave:
    async def test_save_creates_file(self, tmp_path: Path) -> None:
        repo = FileSaveRepository(tmp_path / "saves")
        await repo.save(b"test-data")

        saved = (tmp_path / "saves" / "game_state.sav").read_bytes()
        assert saved == b"test-data"

    async def test_save_creates_directory(self, tmp_path: Path) -> None:
        repo = FileSaveRepository(tmp_path / "deep" / "nested" / "saves")
        await repo.save(b"test-data")

        assert (tmp_path / "deep" / "nested" / "saves" / "game_state.sav").exists()

    async def test_save_overwrites_existing(self, tmp_path: Path) -> None:
        repo = FileSaveRepository(tmp_path / "saves")
        await repo.save(b"first")
        await repo.save(b"second")

        saved = (tmp_path / "saves" / "game_state.sav").read_bytes()
        assert saved == b"second"


class TestFileSaveRepositoryLoad:
    async def test_load_reads_file(self, tmp_path: Path) -> None:
        repo = FileSaveRepository(tmp_path / "saves")
        (tmp_path / "saves").mkdir(parents=True, exist_ok=True)
        (tmp_path / "saves" / "game_state.sav").write_bytes(b"saved-data")

        result = await repo.load()
        assert result == b"saved-data"

    async def test_load_missing_raises(self, tmp_path: Path) -> None:
        repo = FileSaveRepository(tmp_path / "saves")

        with pytest.raises(FileNotFoundError):
            await repo.load()


class TestFileSaveRepositoryRoundTrip:
    async def test_save_then_load(self, tmp_path: Path) -> None:
        repo = FileSaveRepository(tmp_path / "saves")
        original = b"\x00\x01\x02\x03" * 1000

        await repo.save(original)
        loaded = await repo.load()

        assert loaded == original
