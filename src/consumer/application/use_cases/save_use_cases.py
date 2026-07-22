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
from consumer.domain.enums import SessionState


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
        if session.current_state != SessionState.RUNNING:
            return AutosaveResponse(
                last_save_at=datetime.now(tz=timezone.utc), save_count=0
            )
        session.create_snapshot()
        data = await self._snapshot_port.create_snapshot()
        await self._save_repository.save(data)
        metadata = session.record_save(datetime.now(tz=timezone.utc))
        await self._save_repository.save_metadata(SaveMapper.metadata_to_dict(metadata))
        session.restore_snapshot()
        return SaveMapper.to_autosave_response(metadata)


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
        metadata = session.record_save(datetime.now(tz=timezone.utc))
        await self._save_repository.save_metadata(SaveMapper.metadata_to_dict(metadata))
        session.restore_snapshot()
        return SaveMapper.to_manual_save_response(metadata)
