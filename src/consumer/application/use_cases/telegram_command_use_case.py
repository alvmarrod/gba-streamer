from __future__ import annotations

from typing import Awaitable, Callable

from consumer.application.dto.telegram import TelegramEvent
from consumer.application.ports.telegram_message_port import TelegramMessagePort
from consumer.application.use_cases.administration_use_cases import (
    ChangeControlModeUseCase,
)
from consumer.application.use_cases.monitoring_use_cases import GetStatusUseCase
from consumer.application.use_cases.session_use_cases import (
    PauseSessionUseCase,
    ResumeSessionUseCase,
    StartSessionUseCase,
    StopSessionUseCase,
)
from consumer.domain.enums import ControlMode


class HandleTelegramCommandUseCase:
    def __init__(
        self,
        start_session: StartSessionUseCase,
        stop_session: StopSessionUseCase,
        pause_session: PauseSessionUseCase,
        resume_session: ResumeSessionUseCase,
        change_control_mode: ChangeControlModeUseCase,
        get_status: GetStatusUseCase,
        port: TelegramMessagePort,
    ) -> None:
        self._start_session = start_session
        self._stop_session = stop_session
        self._pause_session = pause_session
        self._resume_session = resume_session
        self._change_control_mode = change_control_mode
        self._get_status = get_status
        self._port = port

    async def execute(self, event: TelegramEvent) -> None:
        command = event.command
        if command is None:
            return

        handler = _COMMAND_MAP.get(command)
        if handler is None:
            await self._port.respond(
                bot_id=event.bot_id,
                chat_id=event.chat_id,
                response_type="text",
                payload={"text": f"Unknown command: /{command}"},
                correlation_id=event.event_id,
            )
            return

        await handler(self, event)


async def _handle_start(
    self: HandleTelegramCommandUseCase, event: TelegramEvent
) -> None:
    from consumer.application.dto.session import StartSessionRequest
    from datetime import timedelta

    await self._start_session.execute(
        StartSessionRequest(
            control_mode=ControlMode.FIFO,
            voting_interval=timedelta(seconds=30),
            autosave_interval=timedelta(seconds=15),
        )
    )
    await self._port.respond(
        bot_id=event.bot_id,
        chat_id=event.chat_id,
        response_type="text",
        payload={"text": "Session started in FIFO mode."},
        correlation_id=event.event_id,
    )


async def _handle_stop(
    self: HandleTelegramCommandUseCase, event: TelegramEvent
) -> None:
    from consumer.application.dto.session import StopSessionRequest

    await self._stop_session.execute(StopSessionRequest())
    await self._port.respond(
        bot_id=event.bot_id,
        chat_id=event.chat_id,
        response_type="text",
        payload={"text": "Session stopped."},
        correlation_id=event.event_id,
    )


async def _handle_pause(
    self: HandleTelegramCommandUseCase, event: TelegramEvent
) -> None:
    from consumer.application.dto.session import PauseSessionRequest

    await self._pause_session.execute(PauseSessionRequest())
    await self._port.respond(
        bot_id=event.bot_id,
        chat_id=event.chat_id,
        response_type="text",
        payload={"text": "Session paused."},
        correlation_id=event.event_id,
    )


async def _handle_resume(
    self: HandleTelegramCommandUseCase, event: TelegramEvent
) -> None:
    from consumer.application.dto.session import ResumeSessionRequest

    await self._resume_session.execute(ResumeSessionRequest())
    await self._port.respond(
        bot_id=event.bot_id,
        chat_id=event.chat_id,
        response_type="text",
        payload={"text": "Session resumed."},
        correlation_id=event.event_id,
    )


async def _handle_fifo(
    self: HandleTelegramCommandUseCase, event: TelegramEvent
) -> None:
    from consumer.application.dto.administration import (
        ChangeControlModeRequest,
    )

    await self._change_control_mode.execute(
        ChangeControlModeRequest(control_mode=ControlMode.FIFO)
    )
    await self._port.respond(
        bot_id=event.bot_id,
        chat_id=event.chat_id,
        response_type="text",
        payload={"text": "Control mode changed to FIFO."},
        correlation_id=event.event_id,
    )


async def _handle_voting(
    self: HandleTelegramCommandUseCase, event: TelegramEvent
) -> None:
    from consumer.application.dto.administration import (
        ChangeControlModeRequest,
    )

    await self._change_control_mode.execute(
        ChangeControlModeRequest(control_mode=ControlMode.VOTING)
    )
    await self._port.respond(
        bot_id=event.bot_id,
        chat_id=event.chat_id,
        response_type="text",
        payload={"text": "Control mode changed to Voting."},
        correlation_id=event.event_id,
    )


async def _handle_status(
    self: HandleTelegramCommandUseCase, event: TelegramEvent
) -> None:
    from consumer.application.dto.monitoring import StatusRequest

    response = await self._get_status.execute(StatusRequest())
    text = (
        f"Session: {response.session_state.name}\n"
        f"Mode: {response.control_mode.name}\n"
        f"Players: {response.connected_players} "
        f"(total seen: {response.total_players_seen})\n"
        f"Commands: {response.total_commands}\n"
        f"Frames: {response.frames_executed}\n"
        f"Votes: {response.votes_processed}"
    )
    await self._port.respond(
        bot_id=event.bot_id,
        chat_id=event.chat_id,
        response_type="text",
        payload={"text": text},
        correlation_id=event.event_id,
    )


_COMMAND_MAP: dict[str, Callable[..., Awaitable[None]]] = {
    "start": _handle_start,
    "stop": _handle_stop,
    "pause": _handle_pause,
    "resume": _handle_resume,
    "fifo": _handle_fifo,
    "voting": _handle_voting,
    "status": _handle_status,
}
