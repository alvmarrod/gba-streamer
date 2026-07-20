from __future__ import annotations

from datetime import timedelta
from uuid import uuid4

import pytest

from consumer.application.dto.player import (
    ConnectPlayerRequest,
    DisconnectPlayerRequest,
)
from consumer.application.ports.game_session_provider import GameSessionProvider
from consumer.application.use_cases.player_use_cases import (
    ConnectPlayerUseCase,
    DisconnectPlayerUseCase,
)
from consumer.domain.entities.game_session import GameSession
from consumer.domain.entities.player import Player
from consumer.domain.enums import ControlMode
from consumer.domain.exceptions import PlayerNotConnectedException
from consumer.domain.value_objects import (
    PlayerId,
    SessionConfiguration,
    SessionId,
)


def _make_session() -> GameSession:
    config = SessionConfiguration(
        control_mode=ControlMode.FIFO,
        voting_interval=timedelta(seconds=1),
        autosave_interval=timedelta(seconds=15),
    )
    return GameSession(
        session_id=SessionId(value=uuid4()),
        configuration=config,
    )


class StubSessionProvider(GameSessionProvider):
    def __init__(self, session: GameSession) -> None:
        self._session = session

    async def get_session(self) -> GameSession:
        return self._session


class TestConnectPlayerUseCase:
    async def test_connect_player(self) -> None:
        session = _make_session()
        provider = StubSessionProvider(session)
        use_case = ConnectPlayerUseCase(provider)
        pid = uuid4()

        response = await use_case.execute(
            ConnectPlayerRequest(player_id=pid, display_name="Alice")
        )

        assert response.player_id == pid
        assert response.display_name == "Alice"
        assert session.players.count == 1

    async def test_connect_multiple_players(self) -> None:
        session = _make_session()
        provider = StubSessionProvider(session)
        use_case = ConnectPlayerUseCase(provider)

        await use_case.execute(
            ConnectPlayerRequest(player_id=uuid4(), display_name="Alice")
        )
        await use_case.execute(
            ConnectPlayerRequest(player_id=uuid4(), display_name="Bob")
        )

        assert session.players.count == 2


class TestDisconnectPlayerUseCase:
    async def test_disconnect_player(self) -> None:
        session = _make_session()
        pid = uuid4()
        session.connect_player(
            Player(player_id=PlayerId(value=pid), display_name="Alice")
        )
        provider = StubSessionProvider(session)
        use_case = DisconnectPlayerUseCase(provider)

        await use_case.execute(DisconnectPlayerRequest(player_id=pid))

        assert session.players.count == 0

    async def test_disconnect_unknown_raises(self) -> None:
        session = _make_session()
        provider = StubSessionProvider(session)
        use_case = DisconnectPlayerUseCase(provider)

        with pytest.raises(PlayerNotConnectedException):
            await use_case.execute(DisconnectPlayerRequest(player_id=uuid4()))
