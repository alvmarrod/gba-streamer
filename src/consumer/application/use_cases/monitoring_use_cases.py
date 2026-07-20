from __future__ import annotations

from datetime import timedelta

from consumer.application.dto.monitoring import (
    CollectMetricsRequest,
    CollectMetricsResponse,
    HealthCheckRequest,
    HealthCheckResponse,
    StatusRequest,
    StatusResponse,
)
from consumer.application.mappers.monitoring_mapper import MonitoringMapper
from consumer.application.ports.game_session_provider import GameSessionProvider
from consumer.application.ports.health_indicator_port import HealthIndicatorPort
from consumer.application.ports.metrics_publisher_port import (
    MetricsPublisherPort,
)
from consumer.domain.services.metrics_calculator import MetricsCalculator
from consumer.domain.services.session_validator import SessionValidator


class CollectMetricsUseCase:
    def __init__(
        self,
        session_provider: GameSessionProvider,
        metrics_publisher: MetricsPublisherPort,
    ) -> None:
        self._session_provider = session_provider
        self._metrics_publisher = metrics_publisher

    async def execute(
        self,
        request: CollectMetricsRequest,  # noqa: ARG002
        elapsed: timedelta = timedelta(minutes=1),
    ) -> CollectMetricsResponse:
        session = await self._session_provider.get_session()
        snapshot = MetricsCalculator.calculate(session.metrics, elapsed)
        await self._metrics_publisher.publish(snapshot)
        return MonitoringMapper.to_metrics_response(snapshot)


class HealthCheckUseCase:
    def __init__(
        self,
        session_provider: GameSessionProvider,
        health_indicator: HealthIndicatorPort | None = None,
    ) -> None:
        self._session_provider = session_provider
        self._health_indicator = health_indicator

    async def execute(
        self,
        request: HealthCheckRequest,  # noqa: ARG002
    ) -> HealthCheckResponse:
        session = await self._session_provider.get_session()
        is_healthy = True
        try:
            SessionValidator.validate(session)
        except ValueError:
            is_healthy = False

        components: list[dict[str, object]] = []
        if self._health_indicator is not None:
            components = await self._health_indicator.check()
            for c in components:
                if not c.get("healthy"):
                    is_healthy = False

        return MonitoringMapper.to_health_response(
            session_state=session.current_state,
            connected_players=session.players.count,
            is_healthy=is_healthy,
            components=components,
        )


class GetStatusUseCase:
    def __init__(self, session_provider: GameSessionProvider) -> None:
        self._session_provider = session_provider

    async def execute(
        self,
        request: StatusRequest,  # noqa: ARG002
    ) -> StatusResponse:
        session = await self._session_provider.get_session()
        metrics = session.metrics
        return MonitoringMapper.to_status_response(
            session_state=session.current_state,
            control_mode=session.configuration.control_mode,
            connected_players=metrics.connected_players,
            total_players_seen=metrics.total_players_seen,
            total_commands=metrics.total_commands,
            frames_executed=metrics.frames_executed,
            votes_processed=metrics.votes_processed,
        )
