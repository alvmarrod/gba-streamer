from __future__ import annotations

from consumer.domain.composed.exceptions import InvalidSessionStateException
from consumer.domain.value_objects import GameInput, PlayerId


class VoteRound:
    def __init__(self) -> None:
        self._votes: dict[PlayerId, GameInput] = {}
        self._is_open: bool = True
        self._applied: bool = False

    @property
    def is_open(self) -> bool:
        return self._is_open

    @property
    def applied(self) -> bool:
        return self._applied

    @property
    def votes(self) -> dict[PlayerId, GameInput]:
        return dict(self._votes)

    def collect_vote(self, player_id: PlayerId, game_input: GameInput) -> None:
        if not self._is_open:
            raise InvalidSessionStateException("Cannot collect vote on closed round")
        self._votes[player_id] = game_input

    def close(self) -> None:
        self._is_open = False

    def mark_applied(self) -> None:
        self._applied = True
