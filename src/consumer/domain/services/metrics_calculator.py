from __future__ import annotations

from dataclasses import dataclass
from datetime import timedelta

from consumer.domain.composed.metrics import Metrics


@dataclass(frozen=True)
class MetricsSnapshot:
    total_commands: int
    connected_players: int
    total_players_seen: int
    votes_processed: int
    frames_executed: int
    commands_per_minute: float
    active_player_ratio: float


class MetricsCalculator:
    @staticmethod
    def calculate(metrics: Metrics, elapsed: timedelta) -> MetricsSnapshot:
        minutes = max(elapsed.total_seconds() / 60, 1)
        ratio = (
            metrics.connected_players / metrics.total_players_seen
            if metrics.total_players_seen > 0
            else 0.0
        )
        return MetricsSnapshot(
            total_commands=metrics.total_commands,
            connected_players=metrics.connected_players,
            total_players_seen=metrics.total_players_seen,
            votes_processed=metrics.votes_processed,
            frames_executed=metrics.frames_executed,
            commands_per_minute=metrics.total_commands / minutes,
            active_player_ratio=ratio,
        )
