from __future__ import annotations

from consumer.domain.enums import SessionState
from consumer.domain.services.metrics_calculator import MetricsSnapshot

from consumer.application.dto.monitoring import (
    CollectMetricsResponse,
    HealthCheckResponse,
    MetricsCounters,
)


class MonitoringMapper:
    @staticmethod
    def to_metrics_response(snapshot: MetricsSnapshot) -> CollectMetricsResponse:
        counters = MetricsCounters(
            total_commands=snapshot.total_commands,
            connected_players=snapshot.connected_players,
            total_players_seen=snapshot.total_players_seen,
            votes_processed=snapshot.votes_processed,
            frames_executed=snapshot.frames_executed,
        )
        return CollectMetricsResponse(
            counters=counters,
            commands_per_minute=snapshot.commands_per_minute,
            active_player_ratio=snapshot.active_player_ratio,
        )

    @staticmethod
    def to_health_response(
        session_state: SessionState,
        connected_players: int,
        is_healthy: bool,
    ) -> HealthCheckResponse:
        return HealthCheckResponse(
            session_state=session_state,
            connected_players=connected_players,
            is_healthy=is_healthy,
        )
