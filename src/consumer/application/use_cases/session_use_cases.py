from __future__ import annotations

from consumer.application.dto.session import (
    PauseSessionRequest,
    PauseSessionResponse,
    ResumeSessionRequest,
    ResumeSessionResponse,
    RestoreSessionRequest,
    RestoreSessionResponse,
    StartSessionRequest,
    StartSessionResponse,
    StopSessionRequest,
    StopSessionResponse,
)
from consumer.application.mappers.session_mapper import SessionMapper
from consumer.application.ports.game_session_provider import GameSessionProvider
from consumer.application.ports.save_repository_port import SaveRepositoryPort
from consumer.application.ports.snapshot_port import SnapshotPort


class StartSessionUseCase:
    def __init__(
        self,
        session_provider: GameSessionProvider,
        snapshot_port: SnapshotPort,
        save_repository: SaveRepositoryPort,
    ) -> None:
        self._session_provider = session_provider
        self._snapshot_port = snapshot_port
        self._save_repository = save_repository

    async def execute(self, request: StartSessionRequest) -> StartSessionResponse:
        session = await self._session_provider.get_session()
        try:
            data = await self._save_repository.load()
            await self._snapshot_port.restore_snapshot(data)
        except FileNotFoundError:
            pass
        try:
            meta = await self._save_repository.load_metadata()
            from datetime import datetime

            session.restore_metadata(
                last_save_at=datetime.fromisoformat(meta["last_save_at"]),
                save_count=meta["save_count"],
            )
        except (FileNotFoundError, KeyError, ValueError):
            pass
        configuration = SessionMapper.to_session_config(request)
        session.configure(configuration)
        session.start()
        return SessionMapper.to_start_response(
            session.session_id.value, session.current_state
        )


class StopSessionUseCase:
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
        request: StopSessionRequest,  # noqa: ARG002
    ) -> StopSessionResponse:
        session = await self._session_provider.get_session()
        data = await self._snapshot_port.create_snapshot()
        await self._save_repository.save(data)
        session.stop()
        return SessionMapper.to_stop_response(session.current_state)


class PauseSessionUseCase:
    def __init__(self, session_provider: GameSessionProvider) -> None:
        self._session_provider = session_provider

    async def execute(
        self,
        request: PauseSessionRequest,  # noqa: ARG002
    ) -> PauseSessionResponse:
        session = await self._session_provider.get_session()
        session.pause()
        return SessionMapper.to_pause_response(session.current_state)


class ResumeSessionUseCase:
    def __init__(self, session_provider: GameSessionProvider) -> None:
        self._session_provider = session_provider

    async def execute(
        self,
        request: ResumeSessionRequest,  # noqa: ARG002
    ) -> ResumeSessionResponse:
        session = await self._session_provider.get_session()
        session.resume()
        return SessionMapper.to_resume_response(session.current_state)


class RestoreSessionUseCase:
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
        request: RestoreSessionRequest,  # noqa: ARG002
    ) -> RestoreSessionResponse:
        session = await self._session_provider.get_session()
        data = await self._save_repository.load()
        await self._snapshot_port.restore_snapshot(data)
        session.restore_snapshot()
        return SessionMapper.to_restore_response(
            session.session_id.value, session.current_state
        )
