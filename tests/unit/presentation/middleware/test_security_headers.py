from __future__ import annotations

from aiohttp import web  # type: ignore[import-untyped]
from aiohttp.test_utils import TestClient, TestServer  # type: ignore[import-untyped]

from consumer.presentation.middleware.security_headers import (
    security_headers_middleware,
)


def _make_app() -> web.Application:
    app = web.Application()
    app.middlewares.append(security_headers_middleware)  # type: ignore[arg-type]

    async def _ok(request: web.Request) -> web.Response:
        return web.json_response({"ok": True})

    async def _with_custom(request: web.Request) -> web.Response:
        return web.json_response(
            {"ok": True},
            headers={"X-Content-Type-Options": "custom-value"},
        )

    app.router.add_get("/ok", _ok)
    app.router.add_get("/custom", _with_custom)
    return app


class TestSecurityHeaders:
    async def test_sets_default_headers(self) -> None:
        async with TestClient(TestServer(_make_app())) as client:
            resp = await client.get("/ok")
            assert resp.status == 200
            assert resp.headers["X-Content-Type-Options"] == "nosniff"
            assert resp.headers["Referrer-Policy"] == "strict-origin-when-cross-origin"
            assert resp.headers["X-Permitted-Cross-Domain-Policies"] == "none"
            assert "camera=" in resp.headers["Permissions-Policy"]

    async def test_does_not_overwrite_existing_headers(self) -> None:
        async with TestClient(TestServer(_make_app())) as client:
            resp = await client.get("/custom")
            assert resp.status == 200
            assert resp.headers["X-Content-Type-Options"] == "custom-value"

    async def test_no_x_frame_options(self) -> None:
        async with TestClient(TestServer(_make_app())) as client:
            resp = await client.get("/ok")
            assert "X-Frame-Options" not in resp.headers
