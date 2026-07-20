from __future__ import annotations

from aiohttp import web  # type: ignore[import-untyped]

from consumer.application.ports.logger_port import LoggerPort
from consumer.presentation.api.admin import register_admin_routes
from consumer.presentation.api.input import register_input_routes
from consumer.presentation.api.monitor import register_monitor_routes
from consumer.presentation.api.player import register_player_routes
from consumer.presentation.api.session import register_session_routes
from consumer.presentation.api.signalling import register_signalling_routes
from consumer.presentation.webapp.index import register_webapp_routes


def register_routes(
    app: web.Application,
    use_cases: dict[str, object],
    logger: LoggerPort,
) -> None:
    app["use_cases"] = use_cases
    app["logger"] = logger

    register_webapp_routes(app)
    register_session_routes(app)
    register_player_routes(app)
    register_input_routes(app)
    register_admin_routes(app)
    register_monitor_routes(app)
    register_signalling_routes(app)
