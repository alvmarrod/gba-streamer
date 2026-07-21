from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class TelegramEvent:
    event_id: str
    bot_id: str
    event_type: str
    chat_id: int
    user_id: int
    text: str
    command: str | None
    command_args: str
    from_user_name: str
    from_user_username: str | None
    from_user_id: int
    chat_type: str = ""
