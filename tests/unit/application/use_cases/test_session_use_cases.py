from __future__ import annotations

from datetime import timedelta
from uuid import uuid4


from consumer.application.dto.session import (
    PauseSessionRequest,
    ResumeSessionRequest,
    RestoreSessionRequest,
    StartSessionRequest,
    StopSessionRequest,
)
from consumer.application.ports.game_session_provider import GameSessionProvider
from consumer.application.ports.save_repository_port import SaveRepositoryPort
from consumer.application.ports.snapshot_port import SnapshotPort
from consumer.application.use_cases.session_use_cases import (
    PauseSessionUseCase,
    RestoreSessionUseCase,
    ResumeSessionUseCase,
    StartSessionUseCase,
    StopSessionUseCase,
)
from consumer.domain.entities.game_session import GameSession
from consumer.domain.enums import ControlMode, SessionState
from consumer.domain.value_objects import (
    SessionConfiguration,
    SessionId,
)


def _make_session(
    control_mode: ControlMode = ControlMode.FIFO,
) -> GameSession:
    config = SessionConfiguration(
        control_mode=control_mode,
        voting_interval=timedelta(seconds=1),
        autosave_interval=timedelta(seconds=15),
    )
    return GameSession(
        session_id=SessionId(value=uuid4()),
        configuration=config,
    )


class StubSessionProvider(GameSessionProvider):
    def __init__(self, session: GameSession) -> None:
        self._session = session

    async def get_session(self) -> GameSession:
        return self._session


class StubSnapshotPort(SnapshotPort):
    def __init__(self, data: bytes = b"") -> None:
        self._data = data
        self.restored: bytes | None = None

    async def create_snapshot(self) -> bytes:
        return self._data

    async def restore_snapshot(self, data: bytes) -> None:
        self.restored = data


class StubSaveRepository(SaveRepositoryPort):
    def __init__(self, data: bytes = b"save-data") -> None:
        self._data = data
        self.saved: bytes | None = None

    async def save(self, data: bytes) -> None:
        self.saved = data

    async def load(self) -> bytes:
        return self._data


class TestStartSessionUseCase:
    async def test_start_transitions_to_running(self) -> None:
        session = _make_session()
        provider = StubSessionProvider(session)
        use_case = StartSessionUseCase(provider)

        response = await use_case.execute(
            StartSessionRequest(
                control_mode=ControlMode.VOTING,
                voting_interval=timedelta(seconds=30),
                autosave_interval=timedelta(minutes=5),
            )
        )

        assert response.state == SessionState.RUNNING
        assert response.session_id == session.session_id.value
        assert session.configuration.control_mode == ControlMode.VOTING
        assert session.configuration.voting_interval == timedelta(seconds=30)

    async def test_start_applies_configuration(self) -> None:
        session = _make_session(control_mode=ControlMode.FIFO)
        provider = StubSessionProvider(session)
        use_case = StartSessionUseCase(provider)

        await use_case.execute(
            StartSessionRequest(
                control_mode=ControlMode.VOTING,
                voting_interval=timedelta(seconds=10),
                autosave_interval=timedelta(seconds=20),
            )
        )

        assert session.configuration.control_mode == ControlMode.VOTING
        assert session.configuration.voting_interval == timedelta(seconds=10)
        assert session.configuration.autosave_interval == timedelta(seconds=20)


class TestStopSessionUseCase:
    async def test_stop_transitions_to_stopping(self) -> None:
        session = _make_session()
        session.start()
        provider = StubSessionProvider(session)
        use_case = StopSessionUseCase(provider)

        response = await use_case.execute(StopSessionRequest())

        assert response.state == SessionState.STOPPING


class TestPauseSessionUseCase:
    async def test_pause_transitions_to_paused(self) -> None:
        session = _make_session()
        session.start()
        provider = StubSessionProvider(session)
        use_case = PauseSessionUseCase(provider)

        response = await use_case.execute(PauseSessionRequest())

        assert response.state == SessionState.PAUSED


class TestResumeSessionUseCase:
    async def test_resume_transitions_to_running(self) -> None:
        session = _make_session()
        session.start()
        session.pause()
        provider = StubSessionProvider(session)
        use_case = ResumeSessionUseCase(provider)

        response = await use_case.execute(ResumeSessionRequest())

        assert response.state == SessionState.RUNNING


class TestRestoreSessionUseCase:
    async def test_restore_loads_and_restores(self) -> None:
        session = _make_session()
        session.create_snapshot()
        provider = StubSessionProvider(session)
        snapshot_port = StubSnapshotPort(data=b"restored-data")
        save_repo = StubSaveRepository(data=b"save-data")
        use_case = RestoreSessionUseCase(provider, snapshot_port, save_repo)

        response = await use_case.execute(RestoreSessionRequest(save_path="/tmp/save"))

        assert response.session_id == session.session_id.value
        assert response.state == SessionState.STARTING
        assert snapshot_port.restored == b"save-data"
        assert session.save_manager.has_pending_snapshot is False
