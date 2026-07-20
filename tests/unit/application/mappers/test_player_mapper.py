from uuid import uuid4

from consumer.application.dto.player import (
    ConnectPlayerRequest,
    DisconnectPlayerRequest,
)
from consumer.application.mappers.player_mapper import PlayerMapper
from consumer.domain.entities.player import Player
from consumer.domain.value_objects import PlayerId


class TestPlayerMapper:
    def test_to_player(self) -> None:
        pid = uuid4()
        req = ConnectPlayerRequest(player_id=pid, display_name="Alice")
        player = PlayerMapper.to_player(req)

        assert player.player_id == PlayerId(value=pid)
        assert player.display_name == "Alice"

    def test_to_connect_response(self) -> None:
        pid = uuid4()
        player = Player(player_id=PlayerId(value=pid), display_name="Bob")
        resp = PlayerMapper.to_connect_response(player)

        assert resp.player_id == pid
        assert resp.display_name == "Bob"

    def test_to_player_id(self) -> None:
        pid = uuid4()
        req = DisconnectPlayerRequest(player_id=pid)
        player_id = PlayerMapper.to_player_id(req)

        assert player_id == PlayerId(value=pid)
