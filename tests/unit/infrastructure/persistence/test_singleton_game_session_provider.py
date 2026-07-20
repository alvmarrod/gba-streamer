from __future__ import annotations

from datetime import timedelta
from uuid import uuid4

from consumer.domain.entities.game_session import GameSession
from consumer.domain.enums import ControlMode
from consumer.domain.value_objects import SessionConfiguration, SessionId
from consumer.infrastructure.persistence.singleton_game_session_provider import (
    SingletonGameSessionProvider,
)


class TestSingletonGameSessionProvider:
    async def test_returns_same_session(self) -> None:
        config = SessionConfiguration(
            control_mode=ControlMode.FIFO,
            voting_interval=timedelta(seconds=30),
            autosave_interval=timedelta(seconds=15),
        )
        session = GameSession(session_id=SessionId(uuid4()), configuration=config)

        provider = SingletonGameSessionProvider(session)
        result = await provider.get_session()
        assert result is session

    async def test_always_returns_same_instance(self) -> None:
        config = SessionConfiguration(
            control_mode=ControlMode.VOTING,
            voting_interval=timedelta(seconds=10),
            autosave_interval=timedelta(seconds=60),
        )
        session = GameSession(session_id=SessionId(uuid4()), configuration=config)

        provider = SingletonGameSessionProvider(session)
        a = await provider.get_session()
        b = await provider.get_session()
        assert a is b
        assert a is session
