from __future__ import annotations

from unittest.mock import AsyncMock
from uuid import uuid4

from aiohttp import web  # type: ignore[import-untyped]
from aiohttp.test_utils import TestClient, TestServer  # type: ignore[import-untyped]

from consumer.application.dto.player import (
    ConnectPlayerResponse,
    DisconnectPlayerResponse,
)
from consumer.application.use_cases.player_use_cases import (
    ConnectPlayerUseCase,
    DisconnectPlayerUseCase,
)
from consumer.presentation.api.player import register_player_routes
from consumer.presentation.middleware.error_handler import error_handler_middleware


def _make_app(**use_cases: object) -> web.Application:
    app = web.Application()
    app.middlewares.append(error_handler_middleware)
    app["use_cases"] = use_cases
    register_player_routes(app)
    return app


class TestConnectPlayer:
    async def test_returns_201_with_player_info(self) -> None:
        pid = uuid4()
        mock_uc = AsyncMock(spec=ConnectPlayerUseCase)
        mock_uc.execute.return_value = ConnectPlayerResponse(
            player_id=pid, display_name="Alice"
        )
        async with TestClient(TestServer(_make_app(connect_player=mock_uc))) as client:
            resp = await client.post(
                "/api/player/connect",
                json={"player_id": str(pid), "display_name": "Alice"},
            )
            assert resp.status == 201
            body = await resp.json()
            assert body["player_id"] == str(pid)
            assert body["display_name"] == "Alice"

    async def test_missing_player_id_returns_400(self) -> None:
        async with TestClient(
            TestServer(_make_app(connect_player=AsyncMock()))
        ) as client:
            resp = await client.post(
                "/api/player/connect", json={"display_name": "Alice"}
            )
            assert resp.status == 400

    async def test_invalid_uuid_returns_400(self) -> None:
        async with TestClient(
            TestServer(_make_app(connect_player=AsyncMock()))
        ) as client:
            resp = await client.post(
                "/api/player/connect",
                json={"player_id": "not-a-uuid", "display_name": "Alice"},
            )
            assert resp.status == 400

    async def test_missing_display_name_returns_400(self) -> None:
        async with TestClient(
            TestServer(_make_app(connect_player=AsyncMock()))
        ) as client:
            resp = await client.post(
                "/api/player/connect", json={"player_id": str(uuid4())}
            )
            assert resp.status == 400


class TestDisconnectPlayer:
    async def test_returns_200(self) -> None:
        pid = uuid4()
        mock_uc = AsyncMock(spec=DisconnectPlayerUseCase)
        mock_uc.execute.return_value = DisconnectPlayerResponse()
        async with TestClient(
            TestServer(_make_app(disconnect_player=mock_uc))
        ) as client:
            resp = await client.post(
                "/api/player/disconnect", json={"player_id": str(pid)}
            )
            assert resp.status == 200
            body = await resp.json()
            assert body == {}

    async def test_missing_player_id_returns_400(self) -> None:
        async with TestClient(
            TestServer(_make_app(disconnect_player=AsyncMock()))
        ) as client:
            resp = await client.post("/api/player/disconnect", json={})
            assert resp.status == 400
