from __future__ import annotations

from consumer.domain.entities.player import Player
from consumer.domain.value_objects import PlayerId

from consumer.application.dto.player import (
    ConnectPlayerRequest,
    ConnectPlayerResponse,
    DisconnectPlayerRequest,
)


class PlayerMapper:
    @staticmethod
    def to_player(request: ConnectPlayerRequest) -> Player:
        return Player(
            player_id=PlayerId(value=request.player_id),
            display_name=request.display_name,
        )

    @staticmethod
    def to_connect_response(player: Player) -> ConnectPlayerResponse:
        return ConnectPlayerResponse(
            player_id=player.player_id.value,
            display_name=player.display_name,
        )

    @staticmethod
    def to_player_id(request: DisconnectPlayerRequest) -> PlayerId:
        return PlayerId(value=request.player_id)
