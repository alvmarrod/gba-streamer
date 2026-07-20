from __future__ import annotations

from datetime import timedelta

from consumer.application.dto.monitoring import (
    CollectMetricsRequest,
    CollectMetricsResponse,
    HealthCheckRequest,
    HealthCheckResponse,
)
from consumer.application.mappers.monitoring_mapper import MonitoringMapper
from consumer.application.ports.game_session_provider import GameSessionProvider
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
    def __init__(self, session_provider: GameSessionProvider) -> None:
        self._session_provider = session_provider

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
        return MonitoringMapper.to_health_response(
            session_state=session.current_state,
            connected_players=session.players.count,
            is_healthy=is_healthy,
        )
