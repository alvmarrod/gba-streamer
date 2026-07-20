from __future__ import annotations

from consumer.domain.entities.player import Player
from consumer.domain.exceptions import (
    PlayerAlreadyConnectedException,
    PlayerNotConnectedException,
)
from consumer.domain.value_objects import PlayerId


class PlayerManager:
    def __init__(self) -> None:
        self._players: dict[PlayerId, Player] = {}

    def connect(self, player: Player) -> None:
        if player.player_id in self._players:
            raise PlayerAlreadyConnectedException(
                f"Player {player.player_id.value} already connected"
            )
        self._players[player.player_id] = player

    def disconnect(self, player_id: PlayerId) -> Player:
        if player_id not in self._players:
            raise PlayerNotConnectedException(f"Player {player_id.value} not connected")
        return self._players.pop(player_id)

    def get(self, player_id: PlayerId) -> Player | None:
        return self._players.get(player_id)

    @property
    def players(self) -> list[Player]:
        return list(self._players.values())

    @property
    def count(self) -> int:
        return len(self._players)
