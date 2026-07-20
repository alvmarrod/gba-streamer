from datetime import timedelta
from uuid import uuid4

from consumer.domain.entities.player import Player
from consumer.domain.value_objects import PlayerId, PlayerStatistics


def _make_player_id() -> PlayerId:
    return PlayerId(value=uuid4())


class TestPlayer:
    def test_construction_with_defaults(self) -> None:
        pid = _make_player_id()
        p = Player(player_id=pid, display_name="Alice")
        assert p.player_id == pid
        assert p.display_name == "Alice"
        assert p.statistics.submitted_commands == 0
        assert p.statistics.winning_votes == 0
        assert p.statistics.connected_duration == timedelta()

    def test_construction_with_custom_statistics(self) -> None:
        pid = _make_player_id()
        stats = PlayerStatistics(
            submitted_commands=10,
            winning_votes=3,
            connected_duration=timedelta(minutes=5),
        )
        p = Player(player_id=pid, display_name="Bob", statistics=stats)
        assert p.statistics == stats

    def test_equality_by_player_id(self) -> None:
        pid = _make_player_id()
        p1 = Player(player_id=pid, display_name="Alice")
        p2 = Player(player_id=pid, display_name="Bob")
        assert p1 == p2

    def test_inequality_by_player_id(self) -> None:
        p1 = Player(player_id=_make_player_id(), display_name="Alice")
        p2 = Player(player_id=_make_player_id(), display_name="Alice")
        assert p1 != p2
