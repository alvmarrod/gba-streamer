from __future__ import annotations

from aiohttp import web  # type: ignore[import-untyped]

from consumer.application.ports.logger_port import LoggerPort
from consumer.presentation.api import register_routes


class TestRegisterRoutes:
    def test_all_routes_registered(self) -> None:
        app = web.Application()

        class StubLogger(LoggerPort):
            async def debug(self, message: str, **kwargs: object) -> None: ...
            async def info(self, message: str, **kwargs: object) -> None: ...
            async def warning(self, message: str, **kwargs: object) -> None: ...
            async def error(self, message: str, **kwargs: object) -> None: ...

        register_routes(app, {}, StubLogger())
        route_paths = sorted(
            [
                r.get_info().get("path", "")
                for r in app.router.routes()
                if hasattr(r, "get_info")
            ]
        )
        assert "/api/session" in route_paths
        assert "/api/session/start" in route_paths
        assert "/api/session/stop" in route_paths
        assert "/api/session/pause" in route_paths
        assert "/api/session/resume" in route_paths
        assert "/api/player/connect" in route_paths
        assert "/api/player/disconnect" in route_paths
        assert "/api/input" in route_paths
        assert "/api/control-mode" in route_paths
        assert "/api/config/reload" in route_paths
        assert "/api/health" in route_paths
        assert "/api/metrics" in route_paths
        assert "/api/webrtc/offer" in route_paths

    def test_use_cases_stored_in_app(self) -> None:
        app = web.Application()

        class StubLogger(LoggerPort):
            async def debug(self, message: str, **kwargs: object) -> None: ...
            async def info(self, message: str, **kwargs: object) -> None: ...
            async def warning(self, message: str, **kwargs: object) -> None: ...
            async def error(self, message: str, **kwargs: object) -> None: ...

        use_cases: dict[str, object] = {"test": "value"}
        register_routes(app, use_cases, StubLogger())
        assert app["use_cases"] is use_cases
