from __future__ import annotations

from unittest.mock import patch
import os


from consumer.infrastructure.telegram.rabbitmq_adapter import (
    BrokerConfig,
    _normalize_envelope,
)
from consumer.application.dto.telegram import TelegramEvent


class TestBrokerConfig:
    def test_default_values(self) -> None:
        with patch.dict(os.environ, {}, clear=True):
            config = BrokerConfig()
            assert config.amqp_url == "amqp://guest:guest@localhost:5672/"

    def test_custom_values_from_env(self) -> None:
        with patch.dict(
            os.environ,
            {
                "RABBITMQ_HOST": "rabbit.example.com",
                "RABBITMQ_PORT": "5673",
                "RABBITMQ_USER": "admin",
                "RABBITMQ_PASSWORD": "secret",
                "RABBITMQ_VHOST": "/prod",
            },
            clear=True,
        ):
            config = BrokerConfig()
            assert config.amqp_url == "amqp://admin:secret@rabbit.example.com:5673/prod"


class TestNormalizeEnvelope:
    def test_text_message_with_username(self) -> None:
        raw = {
            "event_id": "evt-1",
            "bot_id": "isabot",
            "event_type": "message",
            "chat_id": 12345,
            "user_id": 67890,
            "message_id": 100,
            "text": "hello world",
            "from_user": {
                "id": 67890,
                "is_bot": False,
                "first_name": "John",
                "last_name": None,
                "username": "john_doe",
                "language_code": "en",
            },
            "routing_context": {},
        }
        result = _normalize_envelope(raw)
        assert isinstance(result, TelegramEvent)
        assert result.event_id == "evt-1"
        assert result.bot_id == "isabot"
        assert result.event_type == "message"
        assert result.chat_id == 12345
        assert result.user_id == 67890
        assert result.text == "hello world"
        assert result.command is None
        assert result.command_args == ""
        assert result.from_user_name == "@john_doe"
        assert result.from_user_id == 67890

    def test_command_with_routing_context(self) -> None:
        raw = {
            "event_id": "evt-2",
            "bot_id": "isabot",
            "event_type": "command",
            "chat_id": 12345,
            "user_id": 67890,
            "message_id": 101,
            "text": "/start",
            "from_user": {
                "id": 67890,
                "is_bot": False,
                "first_name": "Alice",
                "username": "alice",
            },
            "routing_context": {"command": "start", "chat_type": "private"},
        }
        result = _normalize_envelope(raw)
        assert result.command == "start"
        assert result.command_args == ""

    def test_command_with_args(self) -> None:
        raw = {
            "event_id": "evt-3",
            "bot_id": "isabot",
            "event_type": "command",
            "chat_id": 12345,
            "user_id": 67890,
            "message_id": 102,
            "text": "/fifo 30",
            "from_user": {"id": 67890, "first_name": "Bob"},
            "routing_context": {"command": "fifo"},
        }
        result = _normalize_envelope(raw)
        assert result.command == "fifo"
        assert result.command_args == "30"

    def test_user_without_username(self) -> None:
        raw = {
            "event_id": "evt-4",
            "bot_id": "isabot",
            "event_type": "message",
            "chat_id": 12345,
            "user_id": 11111,
            "text": "hi",
            "from_user": {"id": 11111, "first_name": "Charlie", "last_name": "Brown"},
            "routing_context": {},
        }
        result = _normalize_envelope(raw)
        assert result.from_user_name == "Charlie Brown"
        assert result.from_user_username is None

    def test_user_without_name(self) -> None:
        raw = {
            "event_id": "evt-5",
            "bot_id": "isabot",
            "event_type": "message",
            "chat_id": 12345,
            "user_id": 99999,
            "text": "?",
            "from_user": {},
            "routing_context": {},
        }
        result = _normalize_envelope(raw)
        assert result.from_user_name == "Unknown"
        assert result.from_user_id == 0

    def test_missing_fields(self) -> None:
        raw = {
            "event_id": "evt-6",
            "chat_id": 54321,
            "user_id": 111,
            "event_type": "message",
            "bot_id": "isabot",
            "from_user": {"id": 111, "username": "tester"},
            "routing_context": {},
        }
        result = _normalize_envelope(raw)
        assert result.event_id == "evt-6"
        assert result.text == ""
        assert result.command is None
        assert result.command_args == ""

    def test_media_message_with_caption(self) -> None:
        raw = {
            "event_id": "evt-7",
            "bot_id": "isabot",
            "event_type": "message",
            "chat_id": 12345,
            "user_id": 67890,
            "message_id": 200,
            "caption": "check this photo",
            "from_user": {"id": 67890, "first_name": "Dave"},
            "routing_context": {"media_type": "photo"},
            "file_id": "abc123",
            "media_url": "https://example.com/photo.jpg",
        }
        result = _normalize_envelope(raw)
        assert result.text == "check this photo"
        assert result.command is None
