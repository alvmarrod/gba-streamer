from dataclasses import dataclass

from consumer.domain.enums import SessionState


@dataclass(frozen=True)
class CollectMetricsRequest:
    pass


@dataclass(frozen=True)
class MetricsCounters:
    total_commands: int
    connected_players: int
    total_players_seen: int
    votes_processed: int
    frames_executed: int


@dataclass(frozen=True)
class CollectMetricsResponse:
    counters: MetricsCounters
    commands_per_minute: float
    active_player_ratio: float


@dataclass(frozen=True)
class HealthCheckRequest:
    pass


@dataclass(frozen=True)
class HealthCheckResponse:
    session_state: SessionState
    connected_players: int
    is_healthy: bool
