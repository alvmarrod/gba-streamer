from consumer.application.mappers.monitoring_mapper import MonitoringMapper
from consumer.domain.enums import SessionState
from consumer.domain.services.metrics_calculator import MetricsSnapshot


class TestMonitoringMapper:
    def test_to_metrics_response(self) -> None:
        snapshot = MetricsSnapshot(
            total_commands=100,
            connected_players=5,
            total_players_seen=8,
            votes_processed=12,
            frames_executed=500,
            commands_per_minute=50.0,
            active_player_ratio=0.625,
        )
        resp = MonitoringMapper.to_metrics_response(snapshot)

        assert resp.counters.total_commands == 100
        assert resp.counters.connected_players == 5
        assert resp.counters.total_players_seen == 8
        assert resp.counters.votes_processed == 12
        assert resp.counters.frames_executed == 500
        assert resp.commands_per_minute == 50.0
        assert resp.active_player_ratio == 0.625

    def test_to_health_response_healthy(self) -> None:
        resp = MonitoringMapper.to_health_response(
            session_state=SessionState.RUNNING,
            connected_players=3,
            is_healthy=True,
        )

        assert resp.session_state == SessionState.RUNNING
        assert resp.connected_players == 3
        assert resp.is_healthy is True

    def test_to_health_response_unhealthy(self) -> None:
        resp = MonitoringMapper.to_health_response(
            session_state=SessionState.STOPPED,
            connected_players=0,
            is_healthy=False,
        )

        assert resp.session_state == SessionState.STOPPED
        assert resp.connected_players == 0
        assert resp.is_healthy is False
