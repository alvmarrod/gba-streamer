from __future__ import annotations

from datetime import datetime, timezone

from consumer.application.dto.save import (
    AutosaveRequest,
    AutosaveResponse,
    ManualSaveRequest,
    ManualSaveResponse,
)
from consumer.application.mappers.save_mapper import SaveMapper
from consumer.application.ports.game_session_provider import GameSessionProvider
from consumer.application.ports.save_repository_port import SaveRepositoryPort
from consumer.application.ports.snapshot_port import SnapshotPort


class AutosaveUseCase:
    def __init__(
        self,
        session_provider: GameSessionProvider,
        snapshot_port: SnapshotPort,
        save_repository: SaveRepositoryPort,
    ) -> None:
        self._session_provider = session_provider
        self._snapshot_port = snapshot_port
        self._save_repository = save_repository

    async def execute(
        self,
        request: AutosaveRequest,  # noqa: ARG002
    ) -> AutosaveResponse:
        session = await self._session_provider.get_session()
        session.create_snapshot()
        data = await self._snapshot_port.create_snapshot()
        await self._save_repository.save(data)
        session.save_manager.update_metadata(datetime.now(tz=timezone.utc))
        session.restore_snapshot()
        assert session.save_manager.metadata is not None
        return SaveMapper.to_autosave_response(session.save_manager.metadata)


class ManualSaveUseCase:
    def __init__(
        self,
        session_provider: GameSessionProvider,
        snapshot_port: SnapshotPort,
        save_repository: SaveRepositoryPort,
    ) -> None:
        self._session_provider = session_provider
        self._snapshot_port = snapshot_port
        self._save_repository = save_repository

    async def execute(
        self,
        request: ManualSaveRequest,  # noqa: ARG002
    ) -> ManualSaveResponse:
        session = await self._session_provider.get_session()
        session.create_snapshot()
        data = await self._snapshot_port.create_snapshot()
        await self._save_repository.save(data)
        session.save_manager.update_metadata(datetime.now(tz=timezone.utc))
        session.restore_snapshot()
        assert session.save_manager.metadata is not None
        return SaveMapper.to_manual_save_response(session.save_manager.metadata)
