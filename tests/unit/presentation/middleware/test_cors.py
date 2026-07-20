from __future__ import annotations

from aiohttp import web  # type: ignore[import-untyped]
from aiohttp.test_utils import TestClient, TestServer  # type: ignore[import-untyped]

from consumer.presentation.middleware.cors import cors_middleware


def _make_app() -> web.Application:
    app = web.Application()
    app.middlewares.append(cors_middleware)  # type: ignore[arg-type]

    async def _ok(request: web.Request) -> web.Response:
        return web.json_response({"ok": True})

    app.router.add_get("/ok", _ok)
    app.router.add_post("/ok", _ok)
    return app


class TestCorsMiddleware:
    async def test_sets_headers_for_telegram_origin(self) -> None:
        async with TestClient(TestServer(_make_app())) as client:
            resp = await client.get(
                "/ok", headers={"Origin": "https://web.telegram.org"}
            )
            assert resp.status == 200
            assert (
                resp.headers["Access-Control-Allow-Origin"]
                == "https://web.telegram.org"
            )
            assert resp.headers["Access-Control-Allow-Credentials"] == "true"

    async def test_handles_preflight(self) -> None:
        async with TestClient(TestServer(_make_app())) as client:
            resp = await client.options(
                "/ok", headers={"Origin": "https://web.telegram.org"}
            )
            assert resp.status == 204
            assert (
                resp.headers["Access-Control-Allow-Origin"]
                == "https://web.telegram.org"
            )
            assert "GET" in resp.headers["Access-Control-Allow-Methods"]
            assert "POST" in resp.headers["Access-Control-Allow-Methods"]
            assert "Content-Type" in resp.headers["Access-Control-Allow-Headers"]

    async def test_no_header_for_non_telegram_origin(self) -> None:
        async with TestClient(TestServer(_make_app())) as client:
            resp = await client.get("/ok", headers={"Origin": "https://evil.com"})
            assert "Access-Control-Allow-Origin" not in resp.headers
            assert resp.status == 200

    async def test_no_header_when_no_origin(self) -> None:
        async with TestClient(TestServer(_make_app())) as client:
            resp = await client.get("/ok")
            assert "Access-Control-Allow-Origin" not in resp.headers
            assert resp.status == 200

    async def test_preflight_sets_max_age(self) -> None:
        async with TestClient(TestServer(_make_app())) as client:
            resp = await client.options(
                "/ok", headers={"Origin": "https://web.telegram.org"}
            )
            assert resp.headers["Access-Control-Max-Age"] == "86400"
