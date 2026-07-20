import pytest

from consumer.application.dto.monitoring import (
    CollectMetricsRequest,
    CollectMetricsResponse,
    HealthCheckRequest,
    HealthCheckResponse,
    MetricsCounters,
)
from consumer.domain.enums import SessionState


class TestCollectMetricsDTOs:
    def test_request_construction(self) -> None:
        req = CollectMetricsRequest()
        assert req is not None

    def test_counters_construction(self) -> None:
        c = MetricsCounters(
            total_commands=100,
            connected_players=5,
            total_players_seen=8,
            votes_processed=12,
            frames_executed=500,
        )
        assert c.total_commands == 100
        assert c.connected_players == 5
        assert c.total_players_seen == 8
        assert c.votes_processed == 12
        assert c.frames_executed == 500

    def test_counters_immutability(self) -> None:
        c = MetricsCounters(
            total_commands=100,
            connected_players=5,
            total_players_seen=8,
            votes_processed=12,
            frames_executed=500,
        )
        with pytest.raises(AttributeError):
            c.total_commands = 200  # type: ignore[misc]

    def test_response_construction(self) -> None:
        c = MetricsCounters(
            total_commands=60,
            connected_players=2,
            total_players_seen=3,
            votes_processed=10,
            frames_executed=300,
        )
        resp = CollectMetricsResponse(
            counters=c,
            commands_per_minute=60.0,
            active_player_ratio=2 / 3,
        )
        assert resp.counters is c
        assert resp.commands_per_minute == 60.0
        assert resp.active_player_ratio == pytest.approx(2 / 3)

    def test_response_immutability(self) -> None:
        c = MetricsCounters(
            total_commands=0,
            connected_players=0,
            total_players_seen=0,
            votes_processed=0,
            frames_executed=0,
        )
        resp = CollectMetricsResponse(
            counters=c, commands_per_minute=0.0, active_player_ratio=0.0
        )
        with pytest.raises(AttributeError):
            resp.commands_per_minute = 1.0  # type: ignore[misc]


class TestHealthCheckDTOs:
    def test_request_construction(self) -> None:
        req = HealthCheckRequest()
        assert req is not None

    def test_response_construction(self) -> None:
        resp = HealthCheckResponse(
            session_state=SessionState.RUNNING,
            connected_players=3,
            is_healthy=True,
        )
        assert resp.session_state == SessionState.RUNNING
        assert resp.connected_players == 3
        assert resp.is_healthy is True

    def test_response_immutability(self) -> None:
        resp = HealthCheckResponse(
            session_state=SessionState.RUNNING,
            connected_players=3,
            is_healthy=True,
        )
        with pytest.raises(AttributeError):
            resp.is_healthy = False  # type: ignore[misc]
