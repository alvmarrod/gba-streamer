from __future__ import annotations

from typing import Awaitable, Callable

from consumer.application.dto.telegram import TelegramEvent
from consumer.application.ports.authorization_port import AuthorizationPort
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
        auth: AuthorizationPort,
        webapp_url: str = "",
    ) -> None:
        self._start_session = start_session
        self._stop_session = stop_session
        self._pause_session = pause_session
        self._resume_session = resume_session
        self._change_control_mode = change_control_mode
        self._get_status = get_status
        self._port = port
        self._auth = auth
        self._webapp_url = webapp_url

    async def execute(self, event: TelegramEvent) -> None:
        command = event.command
        if command is None:
            return

        if command not in _COMMAND_MAP:
            await self._port.respond(
                bot_id=event.bot_id,
                chat_id=event.chat_id,
                response_type="text",
                payload={"text": f"Unknown command: /{command}"},
                correlation_id=event.event_id,
            )
            return

        if command != "gb-status" and not self._auth.is_admin(event.from_user_id):
            await self._port.respond(
                bot_id=event.bot_id,
                chat_id=event.chat_id,
                response_type="text",
                payload={"text": "Unauthorized."},
                correlation_id=event.event_id,
            )
            return

        handler = _COMMAND_MAP[command]
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
    payload: dict[str, object] = {"text": "Session started in FIFO mode."}
    if self._webapp_url:
        payload["reply_markup"] = {
            "inline_keyboard": [
                [{"text": "Play", "web_app": {"url": self._webapp_url}}]
            ]
        }
    await self._port.respond(
        bot_id=event.bot_id,
        chat_id=event.chat_id,
        response_type="text",
        payload=payload,
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
    "gb-start": _handle_start,
    "gb-stop": _handle_stop,
    "gb-pause": _handle_pause,
    "gb-resume": _handle_resume,
    "gb-fifo": _handle_fifo,
    "gb-voting": _handle_voting,
    "gb-status": _handle_status,
}
