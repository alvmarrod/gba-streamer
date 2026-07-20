from __future__ import annotations

from unittest.mock import AsyncMock

from aiohttp import web  # type: ignore[import-untyped]
from aiohttp.test_utils import TestClient, TestServer  # type: ignore[import-untyped]

from consumer.application.dto.monitoring import (
    CollectMetricsResponse,
    HealthCheckResponse,
    MetricsCounters,
)
from consumer.application.use_cases.monitoring_use_cases import (
    CollectMetricsUseCase,
    HealthCheckUseCase,
)
from consumer.domain.enums import SessionState
from consumer.presentation.api.monitor import register_monitor_routes
from consumer.presentation.middleware.error_handler import error_handler_middleware


def _make_app(**use_cases: object) -> web.Application:
    app = web.Application()
    app.middlewares.append(error_handler_middleware)
    app["use_cases"] = use_cases
    register_monitor_routes(app)
    return app


class TestHealthCheck:
    async def test_returns_health(self) -> None:
        mock_uc = AsyncMock(spec=HealthCheckUseCase)
        mock_uc.execute.return_value = HealthCheckResponse(
            session_state=SessionState.RUNNING,
            connected_players=3,
            is_healthy=True,
            components=[],
        )
        async with TestClient(TestServer(_make_app(health_check=mock_uc))) as client:
            resp = await client.get("/api/health")
            assert resp.status == 200
            body = await resp.json()
            assert body["session_state"] == "RUNNING"
            assert body["connected_players"] == 3
            assert body["is_healthy"] is True

    async def test_unhealthy_session(self) -> None:
        mock_uc = AsyncMock(spec=HealthCheckUseCase)
        mock_uc.execute.return_value = HealthCheckResponse(
            session_state=SessionState.STOPPED,
            connected_players=0,
            is_healthy=False,
            components=[],
        )
        async with TestClient(TestServer(_make_app(health_check=mock_uc))) as client:
            resp = await client.get("/api/health")
            assert resp.status == 200
            body = await resp.json()
            assert body["is_healthy"] is False


class TestCollectMetrics:
    async def test_returns_metrics(self) -> None:
        mock_uc = AsyncMock(spec=CollectMetricsUseCase)
        mock_uc.execute.return_value = CollectMetricsResponse(
            counters=MetricsCounters(
                total_commands=100,
                connected_players=5,
                total_players_seen=10,
                votes_processed=20,
                frames_executed=1000,
            ),
            commands_per_minute=15.5,
            active_player_ratio=0.5,
        )
        async with TestClient(TestServer(_make_app(collect_metrics=mock_uc))) as client:
            resp = await client.get("/api/metrics")
            assert resp.status == 200
            body = await resp.json()
            assert body["counters"]["total_commands"] == 100
            assert body["counters"]["connected_players"] == 5
            assert body["counters"]["total_players_seen"] == 10
            assert body["counters"]["votes_processed"] == 20
            assert body["counters"]["frames_executed"] == 1000
            assert body["commands_per_minute"] == 15.5
            assert body["active_player_ratio"] == 0.5
