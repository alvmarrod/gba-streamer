from __future__ import annotations

from datetime import timedelta


from consumer.application.dto.session import (
    PauseSessionRequest,
    ResumeSessionRequest,
    RestoreSessionRequest,
    StartSessionRequest,
    StopSessionRequest,
)
from consumer.application.use_cases.session_use_cases import (
    PauseSessionUseCase,
    RestoreSessionUseCase,
    ResumeSessionUseCase,
    StartSessionUseCase,
    StopSessionUseCase,
)
from consumer.domain.enums import ControlMode, SessionState

from tests.helpers.factories import make_session
from tests.helpers.stub_providers import (
    StubSaveRepository,
    StubSessionProvider,
    StubSnapshotPort,
)


class TestStartSessionUseCase:
    async def test_start_transitions_to_running(self) -> None:
        session = make_session()
        provider = StubSessionProvider(session)
        snapshot = StubSnapshotPort(data=b"")
        repo = StubSaveRepository(data=b"")
        use_case = StartSessionUseCase(provider, snapshot, repo)

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
        session = make_session(control_mode=ControlMode.FIFO)
        provider = StubSessionProvider(session)
        snapshot = StubSnapshotPort(data=b"")
        repo = StubSaveRepository(data=b"")
        use_case = StartSessionUseCase(provider, snapshot, repo)

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

    async def test_start_restores_from_save(self) -> None:
        session = make_session()
        provider = StubSessionProvider(session)
        snapshot = StubSnapshotPort(data=b"save-data")
        repo = StubSaveRepository(data=b"save-data")
        use_case = StartSessionUseCase(provider, snapshot, repo)

        response = await use_case.execute(
            StartSessionRequest(
                control_mode=ControlMode.FIFO,
                voting_interval=timedelta(seconds=30),
                autosave_interval=timedelta(seconds=15),
            )
        )

        assert snapshot.restored == b"save-data"
        assert response.state == SessionState.RUNNING

    async def test_start_handles_missing_save(self) -> None:
        session = make_session()
        provider = StubSessionProvider(session)
        snapshot = StubSnapshotPort(data=b"")
        repo = StubSaveRepository(data=b"", raise_not_found=True)
        use_case = StartSessionUseCase(provider, snapshot, repo)

        response = await use_case.execute(
            StartSessionRequest(
                control_mode=ControlMode.FIFO,
                voting_interval=timedelta(seconds=30),
                autosave_interval=timedelta(seconds=15),
            )
        )

        assert response.state == SessionState.RUNNING
        assert snapshot.restored is None


class TestStopSessionUseCase:
    async def test_stop_transitions_to_stopped(self) -> None:
        session = make_session()
        await session.start()
        provider = StubSessionProvider(session)
        snapshot = StubSnapshotPort(data=b"final-save")
        repo = StubSaveRepository()
        use_case = StopSessionUseCase(provider, snapshot, repo)

        response = await use_case.execute(StopSessionRequest())

        assert response.state == SessionState.STOPPED
        assert repo.saved == b"final-save"


class TestPauseSessionUseCase:
    async def test_pause_transitions_to_paused(self) -> None:
        session = make_session()
        await session.start()
        provider = StubSessionProvider(session)
        use_case = PauseSessionUseCase(provider)

        response = await use_case.execute(PauseSessionRequest())

        assert response.state == SessionState.PAUSED


class TestResumeSessionUseCase:
    async def test_resume_transitions_to_running(self) -> None:
        session = make_session()
        await session.start()
        await session.pause()
        provider = StubSessionProvider(session)
        use_case = ResumeSessionUseCase(provider)

        response = await use_case.execute(ResumeSessionRequest())

        assert response.state == SessionState.RUNNING


class TestRestoreSessionUseCase:
    async def test_restore_loads_and_restores(self) -> None:
        session = make_session()
        await session.create_snapshot()
        provider = StubSessionProvider(session)
        snapshot_port = StubSnapshotPort(data=b"restored-data")
        save_repo = StubSaveRepository(data=b"save-data")
        use_case = RestoreSessionUseCase(provider, snapshot_port, save_repo)

        response = await use_case.execute(RestoreSessionRequest(save_path="/tmp/save"))

        assert response.session_id == session.session_id.value
        assert response.state == SessionState.STARTING
        assert snapshot_port.restored == b"save-data"
        assert session.save_manager.has_pending_snapshot is False
