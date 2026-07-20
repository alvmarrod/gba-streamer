from __future__ import annotations

import json
import os
import time
import uuid
from typing import Any

import aio_pika  # type: ignore[import-untyped]
from aio_pika.abc import (
    AbstractChannel,
    AbstractExchange,
    AbstractQueue,
    AbstractRobustConnection,
)  # type: ignore[import-untyped]

from consumer.application.ports.telegram_message_port import TelegramMessagePort

_QUEUE_NAME = "goalkeeper.gba_streamer"
_ROUTING_KEY = "incoming.events.isabot.commands"


class BrokerConfig:
    def __init__(self) -> None:
        self.host = os.environ.get("RABBITMQ_HOST", "localhost")
        self.port = int(os.environ.get("RABBITMQ_PORT", "5672"))
        self.user = os.environ.get("RABBITMQ_USER", "guest")
        self.password = os.environ.get("RABBITMQ_PASSWORD", "guest")
        self.vhost = os.environ.get("RABBITMQ_VHOST", "/")

    @property
    def amqp_url(self) -> str:
        return f"amqp://{self.user}:{self.password}@{self.host}:{self.port}{self.vhost}"


class RabbitMQTelegramAdapter(TelegramMessagePort):
    def __init__(self, config: BrokerConfig | None = None) -> None:
        self._config = config or BrokerConfig()
        self._connection: AbstractRobustConnection | None = None
        self._channel: AbstractChannel | None = None
        self._events_exchange: AbstractExchange | None = None
        self._responses_exchange: AbstractExchange | None = None
        self._queue: AbstractQueue | None = None
        self._handler: object | None = None

    async def connect(self) -> None:
        self._connection = await aio_pika.connect_robust(self._config.amqp_url)
        channel = await self._connection.channel()
        assert channel is not None
        self._channel = channel
        self._events_exchange = await channel.declare_exchange(
            "tg-if.events", aio_pika.ExchangeType.TOPIC, durable=True
        )
        self._responses_exchange = await channel.declare_exchange(
            "tg-if.responses", aio_pika.ExchangeType.DIRECT, durable=True
        )
        self._queue = await channel.declare_queue(_QUEUE_NAME, durable=True)

    async def subscribe(self, callback: object) -> None:
        if self._queue is None or self._events_exchange is None:
            return
        await self._queue.bind(self._events_exchange, routing_key=_ROUTING_KEY)
        self._handler = callback

    async def start(self) -> None:
        if self._queue is None or self._handler is None:
            return

        async with self._queue.iterator() as queue_iter:
            async for message in queue_iter:
                async with message.process():
                    try:
                        raw = json.loads(message.body.decode())
                        normalized = _normalize_envelope(raw)
                    except Exception:
                        continue

                    try:
                        callback = self._handler
                        await callback(normalized)  # type: ignore[operator]
                    except Exception:
                        pass

    async def respond(
        self,
        bot_id: str,
        chat_id: int,
        response_type: str,
        payload: dict[str, Any],
        correlation_id: str = "",
    ) -> None:
        if self._responses_exchange is None:
            return
        body = {
            "response_id": str(uuid.uuid4()),
            "correlation_id": correlation_id,
            "timestamp": time.time(),
            "bot_id": bot_id,
            "chat_id": chat_id,
            "response_type": response_type,
            "payload": payload,
        }
        await self._responses_exchange.publish(
            aio_pika.Message(body=json.dumps(body).encode("utf-8")),
            routing_key="response",
        )

    async def close(self) -> None:
        if self._connection:
            await self._connection.close()


def _normalize_envelope(envelope: dict[str, Any]) -> Any:
    from consumer.application.dto.telegram import TelegramEvent

    from_user_raw: dict[str, Any] = envelope.get("from_user") or {}
    username = from_user_raw.get("username")
    if username:
        name = f"@{username}"
    else:
        first = from_user_raw.get("first_name", "")
        last = from_user_raw.get("last_name", "")
        name = f"{first} {last}".strip() or "Unknown"

    text = envelope.get("caption") or envelope.get("text") or ""

    routing_context: dict[str, Any] = envelope.get("routing_context", {})
    command = routing_context.get("command")

    args = ""
    if text.startswith("/") and " " in text:
        args = text.split(" ", 1)[1]

    return TelegramEvent(
        event_id=envelope.get("event_id", ""),
        bot_id=envelope.get("bot_id", ""),
        event_type=envelope.get("event_type", ""),
        chat_id=envelope["chat_id"],
        user_id=envelope["user_id"],
        text=text,
        command=command,
        command_args=args,
        from_user_name=name,
        from_user_username=from_user_raw.get("username"),
        from_user_id=from_user_raw.get("id", 0),
    )
