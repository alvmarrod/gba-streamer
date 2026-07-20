from __future__ import annotations

from aiohttp import web  # type: ignore[import-untyped]
from aiohttp.test_utils import TestClient, TestServer  # type: ignore[import-untyped]

from consumer.domain.exceptions import (
    InvalidControlModeException,
    InvalidSessionStateException,
    PlayerAlreadyConnectedException,
    PlayerNotConnectedException,
    SessionNotRunningException,
    VoteAlreadyRunningException,
)
from consumer.presentation.middleware.error_handler import error_handler_middleware


def _make_app(handler: object | None = None) -> web.Application:
    app = web.Application()
    app.middlewares.append(error_handler_middleware)

    async def _ok(request: web.Request) -> web.Response:
        return web.json_response({"ok": True})

    async def _value_error(request: web.Request) -> web.Response:
        raise ValueError("bad input")

    async def _invalid_session(request: web.Request) -> web.Response:
        raise InvalidSessionStateException("wrong state")

    async def _player_already(request: web.Request) -> web.Response:
        raise PlayerAlreadyConnectedException("already connected")

    async def _player_not_found(request: web.Request) -> web.Response:
        raise PlayerNotConnectedException("not found")

    async def _session_not_running(request: web.Request) -> web.Response:
        raise SessionNotRunningException("not running")

    async def _vote_running(request: web.Request) -> web.Response:
        raise VoteAlreadyRunningException("vote in progress")

    async def _control_mode(request: web.Request) -> web.Response:
        raise InvalidControlModeException("bad mode")

    async def _generic_error(request: web.Request) -> web.Response:
        raise RuntimeError("something broke")

    app.router.add_get("/ok", _ok)
    app.router.add_get("/value-error", _value_error)
    app.router.add_get("/invalid-session", _invalid_session)
    app.router.add_get("/player-already", _player_already)
    app.router.add_get("/player-not-found", _player_not_found)
    app.router.add_get("/session-not-running", _session_not_running)
    app.router.add_get("/vote-running", _vote_running)
    app.router.add_get("/control-mode", _control_mode)
    app.router.add_get("/generic-error", _generic_error)
    return app


class TestErrorHandlerSuccess:
    async def test_handler_passes_through(self) -> None:
        async with TestClient(TestServer(_make_app())) as client:
            resp = await client.get("/ok")
            assert resp.status == 200
            body = await resp.json()
            assert body["ok"] is True


class TestErrorHandlerValueError:
    async def test_returns_400(self) -> None:
        async with TestClient(TestServer(_make_app())) as client:
            resp = await client.get("/value-error")
            assert resp.status == 400
            body = await resp.json()
            assert body["error"] == "bad input"


class TestErrorHandlerDomainExceptions:
    async def test_invalid_session_state_returns_409(self) -> None:
        async with TestClient(TestServer(_make_app())) as client:
            resp = await client.get("/invalid-session")
            assert resp.status == 409
            body = await resp.json()
            assert body["error"] == "wrong state"

    async def test_player_already_connected_returns_409(self) -> None:
        async with TestClient(TestServer(_make_app())) as client:
            resp = await client.get("/player-already")
            assert resp.status == 409
            assert "already connected" in (await resp.json())["error"]

    async def test_player_not_connected_returns_404(self) -> None:
        async with TestClient(TestServer(_make_app())) as client:
            resp = await client.get("/player-not-found")
            assert resp.status == 404
            assert "not found" in (await resp.json())["error"]

    async def test_session_not_running_returns_409(self) -> None:
        async with TestClient(TestServer(_make_app())) as client:
            resp = await client.get("/session-not-running")
            assert resp.status == 409

    async def test_vote_already_running_returns_409(self) -> None:
        async with TestClient(TestServer(_make_app())) as client:
            resp = await client.get("/vote-running")
            assert resp.status == 409

    async def test_invalid_control_mode_returns_400(self) -> None:
        async with TestClient(TestServer(_make_app())) as client:
            resp = await client.get("/control-mode")
            assert resp.status == 400


class TestErrorHandlerGeneric:
    async def test_returns_500_for_unknown_exception(self) -> None:
        async with TestClient(TestServer(_make_app())) as client:
            resp = await client.get("/generic-error")
            assert resp.status == 500
            body = await resp.json()
            assert body["error"] == "Internal server error"

    async def test_does_not_expose_internal_details(self) -> None:
        async with TestClient(TestServer(_make_app())) as client:
            resp = await client.get("/generic-error")
            body = await resp.json()
            assert "RuntimeError" not in body["error"]
            assert "something broke" not in body["error"]
