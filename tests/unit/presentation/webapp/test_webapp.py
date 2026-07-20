from __future__ import annotations

from consumer.presentation.webapp.index import get_index_html, register_webapp_routes
from aiohttp import web  # type: ignore[import-untyped]


class TestGetIndexHtml:
    def test_returns_html_content(self) -> None:
        content = get_index_html()
        assert "<!DOCTYPE html>" in content
        assert "GBA Streamer" in content

    def test_contains_video_element(self) -> None:
        content = get_index_html()
        assert "<video" in content

    def test_contains_gamepad(self) -> None:
        content = get_index_html()
        assert 'data-button="a"' in content
        assert 'data-button="b"' in content


class TestRegisterWebappRoutes:
    def test_routes_registered(self) -> None:
        app = web.Application()
        register_webapp_routes(app)
        route_paths = [
            r.get_info().get("path", "")
            for r in app.router.routes()
            if hasattr(r, "get_info")
        ]
        assert "/" in route_paths
