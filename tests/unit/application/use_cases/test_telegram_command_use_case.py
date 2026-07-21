from __future__ import annotations

from typing import Any
from unittest.mock import AsyncMock

from consumer.application.dto.telegram import TelegramEvent
from consumer.application.ports.authorization_port import AuthorizationPort
from consumer.application.ports.telegram_message_port import TelegramMessagePort
from consumer.application.use_cases.telegram_command_use_case import (
    HandleTelegramCommandUseCase,
)


class StubTelegramPort(TelegramMessagePort):
    def __init__(self) -> None:
        self.responses: list[dict[str, Any]] = []

    async def respond(
        self,
        bot_id: str,
        chat_id: int,
        response_type: str,
        payload: dict[str, object],
        correlation_id: str = "",
    ) -> None:
        self.responses.append(
            {
                "bot_id": bot_id,
                "chat_id": chat_id,
                "response_type": response_type,
                "payload": payload,
                "correlation_id": correlation_id,
            }
        )


class StubAuth(AuthorizationPort):
    def __init__(self, allowed: bool = True) -> None:
        self.allowed = allowed

    def is_admin(self, user_id: int) -> bool:
        return self.allowed


def _make_event(
    command: str | None = None,
    text: str = "",
    from_user_id: int = 67890,
    chat_type: str = "private",
) -> TelegramEvent:
    return TelegramEvent(
        event_id="evt-1",
        bot_id="isabot",
        event_type="command" if command else "message",
        chat_id=12345,
        user_id=from_user_id,
        text=text or f"/{command}" if command else text,
        command=command,
        command_args="",
        from_user_name="@tester",
        from_user_username="tester",
        from_user_id=from_user_id,
        chat_type=chat_type,
    )


def _make_uc(**kwargs: Any) -> HandleTelegramCommandUseCase:
    defaults: dict[str, Any] = {
        "start_session": AsyncMock(),
        "stop_session": AsyncMock(),
        "pause_session": AsyncMock(),
        "resume_session": AsyncMock(),
        "change_control_mode": AsyncMock(),
        "get_status": AsyncMock(),
        "port": StubTelegramPort(),
        "auth": StubAuth(),
        "webapp_url": "",
    }
    defaults.update(kwargs)
    return HandleTelegramCommandUseCase(
        start_session=defaults["start_session"],
        stop_session=defaults["stop_session"],
        pause_session=defaults["pause_session"],
        resume_session=defaults["resume_session"],
        change_control_mode=defaults["change_control_mode"],
        get_status=defaults["get_status"],
        port=defaults["port"],
        auth=defaults["auth"],
        webapp_url=defaults["webapp_url"],
    )


class TestHandleTelegramCommandUseCase:
    async def test_fifo_command(self) -> None:
        mock_change_mode = AsyncMock()
        mock_change_mode.execute = AsyncMock()
        port = StubTelegramPort()
        uc = _make_uc(change_control_mode=mock_change_mode, port=port)
        event = _make_event(command="gb_fifo")

        await uc.execute(event)

        mock_change_mode.execute.assert_awaited_once()
        assert len(port.responses) == 1
        assert "FIFO" in port.responses[0]["payload"]["text"]

    async def test_voting_command(self) -> None:
        mock_change_mode = AsyncMock()
        mock_change_mode.execute = AsyncMock()
        port = StubTelegramPort()
        uc = _make_uc(change_control_mode=mock_change_mode, port=port)
        event = _make_event(command="gb_voting")

        await uc.execute(event)

        mock_change_mode.execute.assert_awaited_once()
        assert len(port.responses) == 1
        assert "Voting" in port.responses[0]["payload"]["text"]

    async def test_start_command(self) -> None:
        mock_start = AsyncMock()
        mock_start.execute = AsyncMock()
        port = StubTelegramPort()
        uc = _make_uc(start_session=mock_start, port=port)
        event = _make_event(command="gb_start")

        await uc.execute(event)

        mock_start.execute.assert_awaited_once()
        assert len(port.responses) == 1
        assert "started" in port.responses[0]["payload"]["text"]

    async def test_stop_command(self) -> None:
        mock_stop = AsyncMock()
        mock_stop.execute = AsyncMock()
        port = StubTelegramPort()
        uc = _make_uc(stop_session=mock_stop, port=port)
        event = _make_event(command="gb_stop")

        await uc.execute(event)

        mock_stop.execute.assert_awaited_once()
        assert len(port.responses) == 1
        assert "stopped" in port.responses[0]["payload"]["text"]

    async def test_unknown_command(self) -> None:
        port = StubTelegramPort()
        uc = _make_uc(port=port)
        event = _make_event(command="nonexistent")

        await uc.execute(event)

        assert len(port.responses) == 1
        assert "Unknown command" in port.responses[0]["payload"]["text"]

    async def test_no_command_skips(self) -> None:
        port = StubTelegramPort()
        uc = _make_uc(port=port)
        event = _make_event(command=None, text="just a message")

        await uc.execute(event)

        assert len(port.responses) == 0

    async def test_admin_command_rejected_for_non_admin(self) -> None:
        port = StubTelegramPort()
        uc = _make_uc(port=port, auth=StubAuth(allowed=False))
        event = _make_event(command="gb_start")

        await uc.execute(event)

        assert len(port.responses) == 1
        assert port.responses[0]["payload"]["text"] == "Unauthorized."

    async def test_status_command_allowed_for_non_admin(self) -> None:
        mock_status = AsyncMock()
        from consumer.application.dto.monitoring import StatusResponse
        from consumer.domain.enums import ControlMode, SessionState

        mock_status.execute = AsyncMock(
            return_value=StatusResponse(
                session_state=SessionState.RUNNING,
                control_mode=ControlMode.FIFO,
                connected_players=0,
                total_players_seen=0,
                total_commands=0,
                frames_executed=0,
                votes_processed=0,
                recent_actions=[],
            )
        )
        port = StubTelegramPort()
        uc = _make_uc(get_status=mock_status, port=port, auth=StubAuth(allowed=False))
        event = _make_event(command="gb_status")

        await uc.execute(event)

        assert len(port.responses) == 1
        assert "RUNNING" in port.responses[0]["payload"]["text"]

    async def test_start_private_chat_sends_webapp_button(self) -> None:
        mock_start = AsyncMock()
        mock_start.execute = AsyncMock()
        port = StubTelegramPort()
        uc = _make_uc(
            start_session=mock_start, port=port, webapp_url="https://example.com"
        )
        event = _make_event(command="gb_start", chat_type="private")

        await uc.execute(event)

        assert len(port.responses) == 1
        payload = port.responses[0]["payload"]
        assert "started" in payload["text"]
        markup = payload.get("reply_markup")
        assert markup is not None
        assert markup[0][0]["web_app"]["url"] == "https://example.com"

    async def test_start_group_chat_sends_inline_keyboard(self) -> None:
        mock_start = AsyncMock()
        mock_start.execute = AsyncMock()
        port = StubTelegramPort()
        uc = _make_uc(
            start_session=mock_start, port=port, webapp_url="https://example.com"
        )
        event = _make_event(command="gb_start", chat_type="supergroup")

        await uc.execute(event)

        assert len(port.responses) == 1
        payload = port.responses[0]["payload"]
        assert "started" in payload["text"]
        markup = payload.get("reply_markup")
        assert markup is not None
        assert (
            markup["inline_keyboard"][0][0]["web_app"]["url"] == "https://example.com"
        )
