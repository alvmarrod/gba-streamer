from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class TelegramMessagePort(ABC):
    @abstractmethod
    async def respond(
        self,
        bot_id: str,
        chat_id: int,
        response_type: str,
        payload: dict[str, Any],
        correlation_id: str = "",
    ) -> None: ...
