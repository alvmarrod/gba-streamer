from __future__ import annotations

from consumer.domain.enums import ControlMode, SessionState
from consumer.domain.services.metrics_calculator import MetricsSnapshot

from consumer.application.dto.monitoring import (
    CollectMetricsResponse,
    HealthCheckResponse,
    MetricsCounters,
    StatusResponse,
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

    @staticmethod
    def to_status_response(
        session_state: SessionState,
        control_mode: ControlMode,
        connected_players: int,
        total_players_seen: int,
        total_commands: int,
        frames_executed: int,
        votes_processed: int,
    ) -> StatusResponse:
        return StatusResponse(
            session_state=session_state,
            control_mode=control_mode,
            connected_players=connected_players,
            total_players_seen=total_players_seen,
            total_commands=total_commands,
            frames_executed=frames_executed,
            votes_processed=votes_processed,
        )
