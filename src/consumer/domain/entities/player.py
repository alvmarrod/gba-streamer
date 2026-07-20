from __future__ import annotations

from dataclasses import dataclass, field
from datetime import timedelta

from consumer.domain.value_objects import PlayerId, PlayerStatistics


@dataclass(eq=False)
class Player:
    player_id: PlayerId
    display_name: str
    statistics: PlayerStatistics = field(
        default_factory=lambda: PlayerStatistics(
            submitted_commands=0,
            winning_votes=0,
            connected_duration=timedelta(),
        )
    )

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Player):
            return NotImplemented
        return self.player_id == other.player_id

    def __hash__(self) -> int:
        return hash(self.player_id)
