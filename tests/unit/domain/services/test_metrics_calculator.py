from datetime import timedelta

import pytest

from consumer.domain.composed.metrics import Metrics
from consumer.domain.services.metrics_calculator import MetricsCalculator


class TestMetricsCalculator:
    def test_commands_per_minute(self) -> None:
        metrics = Metrics()
        for _ in range(60):
            metrics.increment_commands()

        result = MetricsCalculator.calculate(metrics, elapsed=timedelta(minutes=1))

        assert result.commands_per_minute == 60.0
        assert result.total_commands == 60

    def test_active_player_ratio(self) -> None:
        metrics = Metrics()
        for _ in range(3):
            metrics.increment_connected_players()
        metrics.decrement_connected_players()

        result = MetricsCalculator.calculate(metrics, elapsed=timedelta(minutes=5))

        assert result.connected_players == 2
        assert result.total_players_seen == 3
        assert result.active_player_ratio == pytest.approx(2 / 3)

    def test_zero_players(self) -> None:
        metrics = Metrics()
        result = MetricsCalculator.calculate(metrics, elapsed=timedelta(minutes=1))

        assert result.active_player_ratio == 0.0
        assert result.commands_per_minute == 0.0

    def test_short_elapsed_clamps_to_one_minute(self) -> None:
        metrics = Metrics()
        metrics.increment_commands()

        result = MetricsCalculator.calculate(metrics, elapsed=timedelta(seconds=1))

        assert result.commands_per_minute == 1.0

    def test_snapshot_fields(self) -> None:
        metrics = Metrics()
        metrics.increment_commands()
        metrics.increment_connected_players()
        metrics.increment_votes_processed()
        metrics.increment_frames_executed()

        result = MetricsCalculator.calculate(metrics, elapsed=timedelta(minutes=1))

        assert result.total_commands == 1
        assert result.connected_players == 1
        assert result.total_players_seen == 1
        assert result.votes_processed == 1
        assert result.frames_executed == 1
