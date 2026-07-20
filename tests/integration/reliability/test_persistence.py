from __future__ import annotations

from pathlib import Path


from consumer.infrastructure.persistence.file_save_repository import (
    FileSaveRepository,
)


class TestPersistenceReliability:
    async def test_100_roundtrips(self, tmp_path: Path) -> None:
        repo = FileSaveRepository(tmp_path)
        for i in range(100):
            data = f"roundtrip-{i}".encode()
            await repo.save(data)
            result = await repo.load()
            assert result == data

    async def test_1000_overwrites(self, tmp_path: Path) -> None:
        repo = FileSaveRepository(tmp_path)
        for i in range(1000):
            await repo.save(f"overwrite-{i}".encode())
        result = await repo.load()
        assert result == f"overwrite-{999}".encode()

    async def test_restart_recovery(self, tmp_path: Path) -> None:
        repo = FileSaveRepository(tmp_path)
        await repo.save(b"recovery-data")

        repo2 = FileSaveRepository(tmp_path)
        result = await repo2.load()
        assert result == b"recovery-data"
