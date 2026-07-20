from __future__ import annotations

from consumer.infrastructure.telegram.rabbitmq_adapter import _normalize_envelope


def test_normalize_command(benchmark: object) -> None:
    raw: dict[str, object] = {
        "event_id": "evt-1",
        "timestamp": 1706543210.123,
        "bot_id": "isabot",
        "event_type": "command",
        "chat_id": 12345,
        "user_id": 67890,
        "message_id": 100,
        "text": "/start",
        "caption": None,
        "command_args": [],
        "from_user": {
            "id": 67890,
            "is_bot": False,
            "first_name": "John",
            "last_name": None,
            "username": "john_doe",
            "language_code": "en",
        },
        "routing_context": {"command": "start", "chat_type": "private"},
        "payload": {},
    }

    benchmark(_normalize_envelope, raw)  # type: ignore[operator]


def test_normalize_media_with_caption(benchmark: object) -> None:
    raw: dict[str, object] = {
        "event_id": "evt-2",
        "timestamp": 1706543215.456,
        "bot_id": "isabot",
        "event_type": "message",
        "chat_id": 12345,
        "user_id": 67890,
        "message_id": 200,
        "text": None,
        "caption": "check this photo",
        "from_user": {
            "id": 67890,
            "is_bot": False,
            "first_name": "Alice",
            "username": "alice",
        },
        "routing_context": {"media_type": "photo"},
        "payload": {},
        "file_id": "abc123",
        "media_url": "https://example.com/photo.jpg",
    }

    benchmark(_normalize_envelope, raw)  # type: ignore[operator]
