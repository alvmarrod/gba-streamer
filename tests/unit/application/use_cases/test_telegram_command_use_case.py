from __future__ import annotations

from typing import Any
from unittest.mock import AsyncMock


from consumer.application.dto.telegram import TelegramEvent
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


def _make_event(command: str | None = None, text: str = "") -> TelegramEvent:
    return TelegramEvent(
        event_id="evt-1",
        bot_id="isabot",
        event_type="command" if command else "message",
        chat_id=12345,
        user_id=67890,
        text=text or f"/{command}" if command else text,
        command=command,
        command_args="",
        from_user_name="@tester",
        from_user_username="tester",
        from_user_id=67890,
    )


class TestHandleTelegramCommandUseCase:
    async def test_fifo_command(self) -> None:
        mock_change_mode = AsyncMock()
        mock_change_mode.execute = AsyncMock()
        port = StubTelegramPort()
        uc = HandleTelegramCommandUseCase(
            AsyncMock(),
            AsyncMock(),
            AsyncMock(),
            AsyncMock(),
            mock_change_mode,
            AsyncMock(),
            port,
        )
        event = _make_event(command="fifo")

        await uc.execute(event)

        mock_change_mode.execute.assert_awaited_once()
        assert len(port.responses) == 1
        assert port.responses[0]["response_type"] == "text"
        assert "FIFO" in port.responses[0]["payload"]["text"]

    async def test_voting_command(self) -> None:
        mock_change_mode = AsyncMock()
        mock_change_mode.execute = AsyncMock()
        port = StubTelegramPort()
        uc = HandleTelegramCommandUseCase(
            AsyncMock(),
            AsyncMock(),
            AsyncMock(),
            AsyncMock(),
            mock_change_mode,
            AsyncMock(),
            port,
        )
        event = _make_event(command="voting")

        await uc.execute(event)

        mock_change_mode.execute.assert_awaited_once()
        assert len(port.responses) == 1
        assert "Voting" in port.responses[0]["payload"]["text"]

    async def test_start_command(self) -> None:
        mock_start = AsyncMock()
        mock_start.execute = AsyncMock()
        port = StubTelegramPort()
        uc = HandleTelegramCommandUseCase(
            mock_start,
            AsyncMock(),
            AsyncMock(),
            AsyncMock(),
            AsyncMock(),
            AsyncMock(),
            port,
        )
        event = _make_event(command="start")

        await uc.execute(event)

        mock_start.execute.assert_awaited_once()
        assert len(port.responses) == 1
        assert "started" in port.responses[0]["payload"]["text"]

    async def test_stop_command(self) -> None:
        mock_stop = AsyncMock()
        mock_stop.execute = AsyncMock()
        port = StubTelegramPort()
        uc = HandleTelegramCommandUseCase(
            AsyncMock(),
            mock_stop,
            AsyncMock(),
            AsyncMock(),
            AsyncMock(),
            AsyncMock(),
            port,
        )
        event = _make_event(command="stop")

        await uc.execute(event)

        mock_stop.execute.assert_awaited_once()
        assert len(port.responses) == 1
        assert "stopped" in port.responses[0]["payload"]["text"]

    async def test_unknown_command(self) -> None:
        port = StubTelegramPort()
        uc = HandleTelegramCommandUseCase(
            AsyncMock(),
            AsyncMock(),
            AsyncMock(),
            AsyncMock(),
            AsyncMock(),
            AsyncMock(),
            port,
        )
        event = _make_event(command="nonexistent")

        await uc.execute(event)

        assert len(port.responses) == 1
        assert "Unknown command" in port.responses[0]["payload"]["text"]

    async def test_no_command_skips(self) -> None:
        port = StubTelegramPort()
        uc = HandleTelegramCommandUseCase(
            AsyncMock(),
            AsyncMock(),
            AsyncMock(),
            AsyncMock(),
            AsyncMock(),
            AsyncMock(),
            port,
        )
        event = _make_event(command=None, text="just a message")

        await uc.execute(event)

        assert len(port.responses) == 0
