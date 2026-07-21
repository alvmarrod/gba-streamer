from uuid import uuid4

import pytest

from consumer.domain.entities.player import Player
from consumer.domain.composed.player_manager import PlayerManager
from consumer.domain.exceptions import (
    PlayerNotConnectedException,
)
from consumer.domain.value_objects import PlayerId


def _make_player(name: str = "Alice") -> Player:
    return Player(player_id=PlayerId(value=uuid4()), display_name=name)


class TestPlayerManager:
    def test_initial_count(self) -> None:
        assert PlayerManager().count == 0

    def test_connect(self) -> None:
        pm = PlayerManager()
        p = _make_player()
        pm.connect(p)
        assert pm.count == 1

    def test_connect_multiple(self) -> None:
        pm = PlayerManager()
        pm.connect(_make_player("Alice"))
        pm.connect(_make_player("Bob"))
        assert pm.count == 2

    def test_connect_duplicate_replaces(self) -> None:
        pm = PlayerManager()
        p = _make_player()
        pm.connect(p)
        pm.connect(p)
        assert pm.count == 1

    def test_disconnect(self) -> None:
        pm = PlayerManager()
        p = _make_player()
        pm.connect(p)
        removed = pm.disconnect(p.player_id)
        assert removed is p
        assert pm.count == 0

    def test_disconnect_unknown_raises(self) -> None:
        with pytest.raises(PlayerNotConnectedException):
            PlayerManager().disconnect(PlayerId(value=uuid4()))

    def test_get_existing(self) -> None:
        pm = PlayerManager()
        p = _make_player()
        pm.connect(p)
        assert pm.get(p.player_id) is p

    def test_get_unknown_returns_none(self) -> None:
        assert PlayerManager().get(PlayerId(value=uuid4())) is None

    def test_players_returns_list(self) -> None:
        pm = PlayerManager()
        p1 = _make_player("Alice")
        p2 = _make_player("Bob")
        pm.connect(p1)
        pm.connect(p2)
        players = pm.players
        assert len(players) == 2
        assert p1 in players
        assert p2 in players

    def test_players_returns_copy(self) -> None:
        pm = PlayerManager()
        pm.connect(_make_player())
        players = pm.players
        players.clear()
        assert pm.count == 1
