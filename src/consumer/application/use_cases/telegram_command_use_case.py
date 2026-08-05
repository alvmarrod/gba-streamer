from __future__ import annotations

from typing import Awaitable, Callable

from consumer.application.dto.telegram import TelegramEvent
from consumer.application.ports.authorization_port import AuthorizationPort
from consumer.application.ports.save_repository_port import SaveRepositoryPort
from consumer.application.ports.telegram_message_port import TelegramMessagePort
from consumer.application.use_cases.administration_use_cases import (
    ChangeControlModeUseCase,
)
from consumer.application.use_cases.monitoring_use_cases import GetStatusUseCase
from consumer.application.use_cases.session_use_cases import (
    PauseSessionUseCase,
    RestoreSessionUseCase,
    ResumeSessionUseCase,
    StartSessionUseCase,
    StopSessionUseCase,
)
from consumer.domain.enums import ControlMode, SessionState


class HandleTelegramCommandUseCase:
    def __init__(
        self,
        start_session: StartSessionUseCase,
        stop_session: StopSessionUseCase,
        pause_session: PauseSessionUseCase,
        resume_session: ResumeSessionUseCase,
        restore_session: RestoreSessionUseCase,
        change_control_mode: ChangeControlModeUseCase,
        get_status: GetStatusUseCase,
        port: TelegramMessagePort,
        auth: AuthorizationPort,
        save_repository: SaveRepositoryPort,
        webapp_url: str = "",
    ) -> None:
        self._start_session = start_session
        self._stop_session = stop_session
        self._pause_session = pause_session
        self._resume_session = resume_session
        self._restore_session = restore_session
        self._change_control_mode = change_control_mode
        self._get_status = get_status
        self._port = port
        self._auth = auth
        self._save_repository = save_repository
        self._webapp_url = webapp_url

    async def execute(self, event: TelegramEvent) -> None:
        command = event.command
        if command is None:
            return

        if command not in _COMMAND_MAP:
            return

        if command != "gb_status" and not self._auth.is_admin(event.from_user_id):
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

    request = StartSessionRequest(
        control_mode=ControlMode.FIFO,
        voting_interval=timedelta(seconds=30),
        autosave_interval=timedelta(seconds=15),
    )
    await self._start_session.execute(request)

    has_save = False
    save_info = ""
    try:
        await self._save_repository.load()
        try:
            meta = await self._save_repository.load_metadata()
            from datetime import datetime

            last_save = datetime.fromisoformat(meta["last_save_at"])
            save_count = meta.get("save_count", "?")
            save_info = (
                f"Save found from {last_save:%Y-%m-%d %H:%M} UTC"
                f" ({save_count} saves).\n"
            )
        except (FileNotFoundError, KeyError, ValueError):
            save_info = "A saved game was found on disk.\n"
        has_save = True
    except (FileNotFoundError, Exception):
        pass

    if has_save:
        from consumer.application.dto.session import PauseSessionRequest

        await self._pause_session.execute(PauseSessionRequest())
        await self._port.respond(
            bot_id=event.bot_id,
            chat_id=event.chat_id,
            response_type="text",
            payload={
                "text": (
                    f"{save_info}"
                    "Session started (paused). Reply "
                    "/gb_restore to load the save, or "
                    "/gb_resume to start fresh."
                )
            },
            correlation_id=event.event_id,
        )
        return

    payload: dict[str, object] = {"text": "Session started in FIFO mode."}
    if self._webapp_url:
        if event.chat_type == "private":
            payload["reply_markup"] = [
                [{"text": "Play", "web_app": {"url": self._webapp_url}}]
            ]
        else:
            payload["reply_markup"] = [[{"text": "Play", "url": self._webapp_url}]]
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


async def _handle_restore(
    self: HandleTelegramCommandUseCase, event: TelegramEvent
) -> None:
    from consumer.application.dto.session import (
        RestoreSessionRequest,
        ResumeSessionRequest,
    )

    try:
        response = await self._restore_session.execute(
            RestoreSessionRequest(save_path="")
        )
        if response.state == SessionState.PAUSED:
            await self._resume_session.execute(ResumeSessionRequest())
            await self._port.respond(
                bot_id=event.bot_id,
                chat_id=event.chat_id,
                response_type="text",
                payload={"text": "Save restored and session resumed."},
                correlation_id=event.event_id,
            )
        else:
            await self._port.respond(
                bot_id=event.bot_id,
                chat_id=event.chat_id,
                response_type="text",
                payload={"text": "Save state restored from disk."},
                correlation_id=event.event_id,
            )
    except FileNotFoundError:
        await self._port.respond(
            bot_id=event.bot_id,
            chat_id=event.chat_id,
            response_type="text",
            payload={"text": "No save file found on disk."},
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
    "gb_start": _handle_start,
    "gb_stop": _handle_stop,
    "gb_pause": _handle_pause,
    "gb_resume": _handle_resume,
    "gb_restore": _handle_restore,
    "gb_fifo": _handle_fifo,
    "gb_voting": _handle_voting,
    "gb_status": _handle_status,
}
