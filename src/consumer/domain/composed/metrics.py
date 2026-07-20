from __future__ import annotations


class Metrics:
    def __init__(self) -> None:
        self._total_commands: int = 0
        self._connected_players: int = 0
        self._votes_processed: int = 0
        self._frames_executed: int = 0

    @property
    def total_commands(self) -> int:
        return self._total_commands

    @property
    def connected_players(self) -> int:
        return self._connected_players

    @property
    def votes_processed(self) -> int:
        return self._votes_processed

    @property
    def frames_executed(self) -> int:
        return self._frames_executed

    def increment_commands(self) -> None:
        self._total_commands += 1

    def increment_connected_players(self) -> None:
        self._connected_players += 1

    def decrement_connected_players(self) -> None:
        self._connected_players -= 1

    def increment_votes_processed(self) -> None:
        self._votes_processed += 1

    def increment_frames_executed(self) -> None:
        self._frames_executed += 1
