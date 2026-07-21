from __future__ import annotations

from uuid import uuid4

import pytest

from consumer.application.dto.gameplay import (
    ResolveInputRequest,
    SubmitInputRequest,
    TickEmulatorRequest,
)
from consumer.application.use_cases.gameplay_use_cases import (
    ResolveInputUseCase,
    SubmitInputUseCase,
    TickEmulatorUseCase,
)
from consumer.domain.enums import Button, ControlMode
from consumer.domain.exceptions import SessionNotRunningException
from consumer.domain.value_objects import (
    PlayerId,
)

from tests.helpers.factories import make_game_input, make_session
from tests.helpers.stub_providers import (
    StubEmulatorControl,
    StubSessionProvider,
    StubVideoPublisher,
)


class TestSubmitInputUseCase:
    async def test_submit_fifo_input(self) -> None:
        session = make_session(control_mode=ControlMode.FIFO)
        session.start()
        provider = StubSessionProvider(session)
        use_case = SubmitInputUseCase(provider)

        await use_case.execute(
            SubmitInputRequest(player_id=uuid4(), button=Button.LEFT)
        )

        assert session.input_queue.size == 1
        assert session.metrics.total_commands == 1

    async def test_submit_voting_input(self) -> None:
        session = make_session(control_mode=ControlMode.VOTING)
        session.start()
        provider = StubSessionProvider(session)
        use_case = SubmitInputUseCase(provider)

        await use_case.execute(SubmitInputRequest(player_id=uuid4(), button=Button.A))

        assert session.current_vote is not None
        assert session.metrics.total_commands == 1

    async def test_submit_when_not_running_raises(self) -> None:
        session = make_session()
        provider = StubSessionProvider(session)
        use_case = SubmitInputUseCase(provider)

        with pytest.raises(SessionNotRunningException):
            await use_case.execute(
                SubmitInputRequest(player_id=uuid4(), button=Button.A)
            )


class TestResolveInputUseCase:
    async def test_resolve_fifo_dequeues_and_executes(self) -> None:
        session = make_session(control_mode=ControlMode.FIFO)
        session.start()
        gi = make_game_input(Button.LEFT)
        session.submit_input(gi)
        provider = StubSessionProvider(session)
        emulator = StubEmulatorControl()
        use_case = ResolveInputUseCase(provider, emulator)

        await use_case.execute(ResolveInputRequest())

        assert len(emulator.executed) == 1
        assert emulator.executed[0] is gi
        assert session.input_queue.size == 0

    async def test_resolve_fifo_empty_queue_returns_empty(self) -> None:
        session = make_session(control_mode=ControlMode.FIFO)
        session.start()
        provider = StubSessionProvider(session)
        emulator = StubEmulatorControl()
        use_case = ResolveInputUseCase(provider, emulator)

        await use_case.execute(ResolveInputRequest())

        assert len(emulator.executed) == 0

    async def test_resolve_voting_resolves_and_executes(self) -> None:
        session = make_session(control_mode=ControlMode.VOTING)
        session.start()
        pid = PlayerId(value=uuid4())
        gi = make_game_input(Button.RIGHT, pid)
        session.submit_input(gi)
        provider = StubSessionProvider(session)
        emulator = StubEmulatorControl()
        use_case = ResolveInputUseCase(provider, emulator)

        await use_case.execute(ResolveInputRequest())

        assert len(emulator.executed) == 1
        assert emulator.executed[0].button == Button.RIGHT

    async def test_resolve_voting_no_vote_round_returns_empty(self) -> None:
        session = make_session(control_mode=ControlMode.VOTING)
        session.start()
        provider = StubSessionProvider(session)
        emulator = StubEmulatorControl()
        use_case = ResolveInputUseCase(provider, emulator)

        await use_case.execute(ResolveInputRequest())

        assert len(emulator.executed) == 0

    async def test_resolve_voting_tie_first_vote_wins(self) -> None:
        session = make_session(control_mode=ControlMode.VOTING)
        session.start()
        pid1 = PlayerId(value=uuid4())
        pid2 = PlayerId(value=uuid4())
        gi1 = make_game_input(Button.LEFT, pid1)
        gi2 = make_game_input(Button.RIGHT, pid2)
        session.submit_input(gi1)
        session.submit_input(gi2)
        provider = StubSessionProvider(session)
        emulator = StubEmulatorControl()
        use_case = ResolveInputUseCase(provider, emulator)

        await use_case.execute(ResolveInputRequest())

        assert emulator.executed[0].button == Button.LEFT


class TestTickEmulatorUseCase:
    async def test_tick_executes_and_publishes(self) -> None:
        session = make_session()
        session.start()
        provider = StubSessionProvider(session)
        emulator = StubEmulatorControl()
        publisher = StubVideoPublisher()
        resolve_input = ResolveInputUseCase(provider, emulator)
        use_case = TickEmulatorUseCase(provider, emulator, publisher, resolve_input)

        await use_case.execute(TickEmulatorRequest())

        assert emulator.tick_count == 1
        assert publisher.publish_count == 1
        assert session.metrics.frames_executed == 1
