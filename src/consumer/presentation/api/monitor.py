from __future__ import annotations

from aiohttp import web  # type: ignore[import-untyped]

from consumer.application.dto.monitoring import (
    CollectMetricsRequest,
    HealthCheckRequest,
)
from consumer.application.use_cases.monitoring_use_cases import (
    CollectMetricsUseCase,
    HealthCheckUseCase,
)
from consumer.presentation.api.mappers import PresentationMapper


async def health_check(request: web.Request) -> web.Response:
    use_case: HealthCheckUseCase = request.app["use_cases"]["health_check"]
    response = await use_case.execute(HealthCheckRequest())
    return web.json_response(
        {
            "session_state": PresentationMapper.enum_name(response.session_state),
            "connected_players": response.connected_players,
            "is_healthy": response.is_healthy,
        }
    )


async def collect_metrics(request: web.Request) -> web.Response:
    use_case: CollectMetricsUseCase = request.app["use_cases"]["collect_metrics"]
    response = await use_case.execute(CollectMetricsRequest())
    return web.json_response(
        {
            "counters": {
                "total_commands": response.counters.total_commands,
                "connected_players": response.counters.connected_players,
                "total_players_seen": response.counters.total_players_seen,
                "votes_processed": response.counters.votes_processed,
                "frames_executed": response.counters.frames_executed,
            },
            "commands_per_minute": response.commands_per_minute,
            "active_player_ratio": response.active_player_ratio,
        }
    )


def register_monitor_routes(app: web.Application) -> None:
    app.router.add_get("/api/health", health_check)
    app.router.add_get("/api/metrics", collect_metrics)
