from __future__ import annotations


from tests.helpers.factories import make_session
from tests.helpers.stub_providers import StubSessionProvider

from consumer.application.dto.save import AutosaveRequest, ManualSaveRequest
from consumer.application.ports.save_repository_port import SaveRepositoryPort
from consumer.application.ports.snapshot_port import SnapshotPort
from consumer.application.use_cases.save_use_cases import (
    AutosaveUseCase,
    ManualSaveUseCase,
)


class StubSnapshotPort(SnapshotPort):
    def __init__(self, data: bytes = b"snapshot-bytes") -> None:
        self._data = data
        self.restored: bytes | None = None

    async def create_snapshot(self) -> bytes:
        return self._data

    async def restore_snapshot(self, data: bytes) -> None:
        self.restored = data


class StubSaveRepository(SaveRepositoryPort):
    def __init__(self) -> None:
        self.saved: bytes | None = None
        self.saved_metadata: dict[str, object] | None = None

    async def save(self, data: bytes) -> None:
        self.saved = data

    async def load(self) -> bytes:
        return b""

    async def save_metadata(self, metadata: dict[str, object]) -> None:
        self.saved_metadata = metadata

    async def load_metadata(self) -> dict[str, object]:
        return {}


class TestAutosaveUseCase:
    async def test_autosave_persists_snapshot(self) -> None:
        session = make_session()
        await session.start()
        provider = StubSessionProvider(session)
        snapshot_port = StubSnapshotPort(data=b"emulator-state")
        save_repo = StubSaveRepository()
        use_case = AutosaveUseCase(provider, snapshot_port, save_repo)

        response = await use_case.execute(AutosaveRequest())

        assert save_repo.saved == b"emulator-state"
        assert session.save_manager.has_pending_snapshot is False
        assert session.save_manager.metadata is not None
        assert session.save_manager.metadata.save_count == 1
        assert response.save_count == 1

    async def test_autosave_increments_count(self) -> None:
        session = make_session()
        await session.start()
        provider = StubSessionProvider(session)
        snapshot_port = StubSnapshotPort()
        save_repo = StubSaveRepository()
        use_case = AutosaveUseCase(provider, snapshot_port, save_repo)

        await use_case.execute(AutosaveRequest())
        response = await use_case.execute(AutosaveRequest())

        assert response.save_count == 2

    async def test_autosave_skips_when_not_running(self) -> None:
        session = make_session()
        provider = StubSessionProvider(session)
        snapshot_port = StubSnapshotPort()
        save_repo = StubSaveRepository()
        use_case = AutosaveUseCase(provider, snapshot_port, save_repo)

        response = await use_case.execute(AutosaveRequest())

        assert save_repo.saved is None
        assert response.save_count == 0


class TestManualSaveUseCase:
    async def test_manual_save_persists_snapshot(self) -> None:
        session = make_session()
        provider = StubSessionProvider(session)
        snapshot_port = StubSnapshotPort(data=b"manual-save")
        save_repo = StubSaveRepository()
        use_case = ManualSaveUseCase(provider, snapshot_port, save_repo)

        response = await use_case.execute(ManualSaveRequest())

        assert save_repo.saved == b"manual-save"
        assert session.save_manager.has_pending_snapshot is False
        assert response.save_count == 1
