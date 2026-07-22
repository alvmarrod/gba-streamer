from __future__ import annotations

from consumer.application.dto.gameplay import (
    ResolveInputRequest,
    ResolveInputResponse,
    SubmitInputRequest,
    SubmitInputResponse,
    TickEmulatorRequest,
    TickEmulatorResponse,
)
from consumer.application.mappers.gameplay_mapper import GameplayMapper
from consumer.application.ports.emulator_control_port import EmulatorControlPort
from consumer.application.ports.game_session_provider import GameSessionProvider
from consumer.application.ports.video_publisher_port import VideoPublisherPort
from consumer.domain.enums import ControlMode, SessionState
from consumer.domain.services.fifo_resolver import FIFOResolver


class SubmitInputUseCase:
    def __init__(self, session_provider: GameSessionProvider) -> None:
        self._session_provider = session_provider

    async def execute(self, request: SubmitInputRequest) -> SubmitInputResponse:
        session = await self._session_provider.get_session()
        game_input = GameplayMapper.to_game_input(request)
        session.submit_input(game_input)
        return SubmitInputResponse()


class ResolveInputUseCase:
    def __init__(
        self,
        session_provider: GameSessionProvider,
        emulator_control: EmulatorControlPort,
    ) -> None:
        self._session_provider = session_provider
        self._emulator_control = emulator_control

    async def execute(
        self,
        request: ResolveInputRequest,  # noqa: ARG002
    ) -> ResolveInputResponse:
        session = await self._session_provider.get_session()
        if session.configuration.control_mode != ControlMode.FIFO:
            return ResolveInputResponse()
        game_input = FIFOResolver.resolve(session.input_queue)
        if game_input is None:
            return ResolveInputResponse()
        await self._emulator_control.execute_input(game_input)
        return ResolveInputResponse()


class TickEmulatorUseCase:
    def __init__(
        self,
        session_provider: GameSessionProvider,
        emulator_control: EmulatorControlPort,
        video_publisher: VideoPublisherPort,
        resolve_input: ResolveInputUseCase,
    ) -> None:
        self._session_provider = session_provider
        self._emulator_control = emulator_control
        self._video_publisher = video_publisher
        self._resolve_input = resolve_input

    async def execute(
        self,
        request: TickEmulatorRequest,  # noqa: ARG002
    ) -> TickEmulatorResponse:
        session = await self._session_provider.get_session()
        if session.current_state != SessionState.RUNNING:
            return TickEmulatorResponse()
        session.record_tick()
        await self._resolve_input.execute(ResolveInputRequest())
        await self._emulator_control.tick()
        await self._video_publisher.publish()
        return TickEmulatorResponse()
