from __future__ import annotations

from datetime import datetime, timedelta, timezone
from uuid import uuid4

import pytest

from consumer.application.dto.gameplay import (
    ResolveInputRequest,
    SubmitInputRequest,
    TickEmulatorRequest,
)
from consumer.application.ports.emulator_control_port import EmulatorControlPort
from consumer.application.ports.game_session_provider import GameSessionProvider
from consumer.application.ports.video_publisher_port import VideoPublisherPort
from consumer.application.use_cases.gameplay_use_cases import (
    ResolveInputUseCase,
    SubmitInputUseCase,
    TickEmulatorUseCase,
)
from consumer.domain.entities.game_session import GameSession
from consumer.domain.enums import Button, ControlMode
from consumer.domain.exceptions import SessionNotRunningException
from consumer.domain.value_objects import (
    GameInput,
    PlayerId,
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


def _make_game_input(
    button: Button = Button.A, player_id: PlayerId | None = None
) -> GameInput:
    return GameInput(
        button=button,
        timestamp=datetime.now(tz=timezone.utc),
        player_id=player_id or PlayerId(value=uuid4()),
    )


class StubSessionProvider(GameSessionProvider):
    def __init__(self, session: GameSession) -> None:
        self._session = session

    async def get_session(self) -> GameSession:
        return self._session


class StubEmulatorControl(EmulatorControlPort):
    def __init__(self) -> None:
        self.executed_inputs: list[GameInput] = []
        self.tick_count: int = 0

    async def execute_input(self, game_input: GameInput) -> None:
        self.executed_inputs.append(game_input)

    async def tick(self) -> None:
        self.tick_count += 1


class StubVideoPublisher(VideoPublisherPort):
    def __init__(self) -> None:
        self.publish_count: int = 0

    async def publish(self) -> None:
        self.publish_count += 1


class TestSubmitInputUseCase:
    async def test_submit_fifo_input(self) -> None:
        session = _make_session(control_mode=ControlMode.FIFO)
        session.start()
        provider = StubSessionProvider(session)
        use_case = SubmitInputUseCase(provider)

        await use_case.execute(
            SubmitInputRequest(player_id=uuid4(), button=Button.LEFT)
        )

        assert session.input_queue.size == 1
        assert session.metrics.total_commands == 1

    async def test_submit_voting_input(self) -> None:
        session = _make_session(control_mode=ControlMode.VOTING)
        session.start()
        provider = StubSessionProvider(session)
        use_case = SubmitInputUseCase(provider)

        await use_case.execute(SubmitInputRequest(player_id=uuid4(), button=Button.A))

        assert session.current_vote is not None
        assert session.metrics.total_commands == 1

    async def test_submit_when_not_running_raises(self) -> None:
        session = _make_session()
        provider = StubSessionProvider(session)
        use_case = SubmitInputUseCase(provider)

        with pytest.raises(SessionNotRunningException):
            await use_case.execute(
                SubmitInputRequest(player_id=uuid4(), button=Button.A)
            )


class TestResolveInputUseCase:
    async def test_resolve_fifo_dequeues_and_executes(self) -> None:
        session = _make_session(control_mode=ControlMode.FIFO)
        session.start()
        gi = _make_game_input(Button.LEFT)
        session.submit_input(gi)
        provider = StubSessionProvider(session)
        emulator = StubEmulatorControl()
        use_case = ResolveInputUseCase(provider, emulator)

        await use_case.execute(ResolveInputRequest())

        assert len(emulator.executed_inputs) == 1
        assert emulator.executed_inputs[0] is gi
        assert session.input_queue.size == 0

    async def test_resolve_fifo_empty_queue_raises(self) -> None:
        session = _make_session(control_mode=ControlMode.FIFO)
        session.start()
        provider = StubSessionProvider(session)
        emulator = StubEmulatorControl()
        use_case = ResolveInputUseCase(provider, emulator)

        with pytest.raises(IndexError):
            await use_case.execute(ResolveInputRequest())

    async def test_resolve_voting_resolves_and_executes(self) -> None:
        session = _make_session(control_mode=ControlMode.VOTING)
        session.start()
        pid = PlayerId(value=uuid4())
        gi = _make_game_input(Button.RIGHT, pid)
        session.submit_input(gi)
        provider = StubSessionProvider(session)
        emulator = StubEmulatorControl()
        use_case = ResolveInputUseCase(provider, emulator)

        await use_case.execute(ResolveInputRequest())

        assert len(emulator.executed_inputs) == 1
        assert emulator.executed_inputs[0].button == Button.RIGHT

    async def test_resolve_voting_no_vote_round_returns_empty(self) -> None:
        session = _make_session(control_mode=ControlMode.VOTING)
        session.start()
        provider = StubSessionProvider(session)
        emulator = StubEmulatorControl()
        use_case = ResolveInputUseCase(provider, emulator)

        await use_case.execute(ResolveInputRequest())

        assert len(emulator.executed_inputs) == 0

    async def test_resolve_voting_tie_first_vote_wins(self) -> None:
        session = _make_session(control_mode=ControlMode.VOTING)
        session.start()
        pid1 = PlayerId(value=uuid4())
        pid2 = PlayerId(value=uuid4())
        gi1 = _make_game_input(Button.LEFT, pid1)
        gi2 = _make_game_input(Button.RIGHT, pid2)
        session.submit_input(gi1)
        session.submit_input(gi2)
        provider = StubSessionProvider(session)
        emulator = StubEmulatorControl()
        use_case = ResolveInputUseCase(provider, emulator)

        await use_case.execute(ResolveInputRequest())

        assert emulator.executed_inputs[0].button == Button.LEFT


class TestTickEmulatorUseCase:
    async def test_tick_executes_and_publishes(self) -> None:
        session = _make_session()
        session.start()
        provider = StubSessionProvider(session)
        emulator = StubEmulatorControl()
        publisher = StubVideoPublisher()
        use_case = TickEmulatorUseCase(provider, emulator, publisher)

        await use_case.execute(TickEmulatorRequest())

        assert emulator.tick_count == 1
        assert publisher.publish_count == 1
        assert session.metrics.frames_executed == 1
