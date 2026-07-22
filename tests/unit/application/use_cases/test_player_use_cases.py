from __future__ import annotations

from uuid import uuid4

import pytest

from tests.helpers.factories import make_session
from tests.helpers.stub_providers import StubSessionProvider

from consumer.application.dto.player import (
    ConnectPlayerRequest,
    DisconnectPlayerRequest,
)
from consumer.application.use_cases.player_use_cases import (
    ConnectPlayerUseCase,
    DisconnectPlayerUseCase,
)
from consumer.domain.entities.player import Player
from consumer.domain.exceptions import PlayerNotConnectedException
from consumer.domain.value_objects import (
    PlayerId,
)


class TestConnectPlayerUseCase:
    async def test_connect_player(self) -> None:
        session = make_session()
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
        session = make_session()
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
        session = make_session()
        pid = uuid4()
        await session.connect_player(
            Player(player_id=PlayerId(value=pid), display_name="Alice")
        )
        provider = StubSessionProvider(session)
        use_case = DisconnectPlayerUseCase(provider)

        await use_case.execute(DisconnectPlayerRequest(player_id=pid))

        assert session.players.count == 0

    async def test_disconnect_unknown_raises(self) -> None:
        session = make_session()
        provider = StubSessionProvider(session)
        use_case = DisconnectPlayerUseCase(provider)

        with pytest.raises(PlayerNotConnectedException):
            await use_case.execute(DisconnectPlayerRequest(player_id=uuid4()))
