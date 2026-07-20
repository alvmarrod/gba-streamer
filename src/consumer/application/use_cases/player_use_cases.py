from __future__ import annotations

from consumer.application.dto.player import (
    ConnectPlayerRequest,
    ConnectPlayerResponse,
    DisconnectPlayerRequest,
    DisconnectPlayerResponse,
)
from consumer.application.mappers.player_mapper import PlayerMapper
from consumer.application.ports.game_session_provider import GameSessionProvider


class ConnectPlayerUseCase:
    def __init__(self, session_provider: GameSessionProvider) -> None:
        self._session_provider = session_provider

    async def execute(self, request: ConnectPlayerRequest) -> ConnectPlayerResponse:
        session = await self._session_provider.get_session()
        player = PlayerMapper.to_player(request)
        session.connect_player(player)
        return PlayerMapper.to_connect_response(player)


class DisconnectPlayerUseCase:
    def __init__(self, session_provider: GameSessionProvider) -> None:
        self._session_provider = session_provider

    async def execute(
        self, request: DisconnectPlayerRequest
    ) -> DisconnectPlayerResponse:
        session = await self._session_provider.get_session()
        player_id = PlayerMapper.to_player_id(request)
        session.disconnect_player(player_id)
        return DisconnectPlayerResponse()
