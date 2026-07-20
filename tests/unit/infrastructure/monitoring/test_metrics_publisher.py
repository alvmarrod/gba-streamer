from __future__ import annotations

import json
from unittest.mock import AsyncMock

import pytest

from consumer.domain.services.metrics_calculator import MetricsSnapshot
from consumer.infrastructure.monitoring.metrics_publisher import MetricsPublisher


@pytest.fixture
def mock_logger() -> AsyncMock:
    return AsyncMock()


@pytest.fixture
def publisher(mock_logger: AsyncMock) -> MetricsPublisher:
    return MetricsPublisher(mock_logger)


@pytest.fixture
def sample_snapshot() -> MetricsSnapshot:
    return MetricsSnapshot(
        total_commands=150,
        connected_players=5,
        total_players_seen=12,
        votes_processed=30,
        frames_executed=500,
        commands_per_minute=25.5,
        active_player_ratio=0.42,
    )


class TestMetricsPublisher:
    async def test_publish_logs_json(
        self,
        publisher: MetricsPublisher,
        mock_logger: AsyncMock,
        sample_snapshot: MetricsSnapshot,
    ) -> None:
        await publisher.publish(sample_snapshot)

        mock_logger.info.assert_called_once()
        logged_str = mock_logger.info.call_args[0][0]
        payload = json.loads(logged_str)

        assert payload["total_commands"] == 150
        assert payload["connected_players"] == 5
        assert payload["total_players_seen"] == 12
        assert payload["votes_processed"] == 30
        assert payload["frames_executed"] == 500
        assert payload["commands_per_minute"] == 25.5
        assert payload["active_player_ratio"] == 0.42

    async def test_publish_zero_metrics(
        self, publisher: MetricsPublisher, mock_logger: AsyncMock
    ) -> None:
        snapshot = MetricsSnapshot(
            total_commands=0,
            connected_players=0,
            total_players_seen=0,
            votes_processed=0,
            frames_executed=0,
            commands_per_minute=0.0,
            active_player_ratio=0.0,
        )
        await publisher.publish(snapshot)

        logged_str = mock_logger.info.call_args[0][0]
        payload = json.loads(logged_str)
        assert payload["total_commands"] == 0
        assert payload["active_player_ratio"] == 0.0
