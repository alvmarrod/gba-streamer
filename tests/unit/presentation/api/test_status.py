from __future__ import annotations

from unittest.mock import AsyncMock

from aiohttp import web  # type: ignore[import-untyped]
from aiohttp.test_utils import TestClient, TestServer  # type: ignore[import-untyped]

from consumer.application.dto.monitoring import StatusResponse
from consumer.application.use_cases.monitoring_use_cases import GetStatusUseCase
from consumer.domain.enums import ControlMode, SessionState
from consumer.presentation.api.monitor import register_monitor_routes
from consumer.presentation.middleware.error_handler import error_handler_middleware


def _make_app(**use_cases: object) -> web.Application:
    app = web.Application()
    app.middlewares.append(error_handler_middleware)
    app["use_cases"] = use_cases
    register_monitor_routes(app)
    return app


class TestGetStatus:
    async def test_returns_status_fields(self) -> None:
        mock_uc = AsyncMock(spec=GetStatusUseCase)
        mock_uc.execute.return_value = StatusResponse(
            session_state=SessionState.RUNNING,
            control_mode=ControlMode.FIFO,
            connected_players=3,
            total_players_seen=10,
            total_commands=150,
            frames_executed=2000,
            votes_processed=5,
        )
        async with TestClient(TestServer(_make_app(get_status=mock_uc))) as client:
            resp = await client.get("/api/status")
            assert resp.status == 200
            body = await resp.json()
            assert body["session_state"] == "RUNNING"
            assert body["control_mode"] == "FIFO"
            assert body["connected_players"] == 3
            assert body["total_players_seen"] == 10
            assert body["total_commands"] == 150
            assert body["frames_executed"] == 2000
            assert body["votes_processed"] == 5

    async def test_returns_voting_mode(self) -> None:
        mock_uc = AsyncMock(spec=GetStatusUseCase)
        mock_uc.execute.return_value = StatusResponse(
            session_state=SessionState.RUNNING,
            control_mode=ControlMode.VOTING,
            connected_players=1,
            total_players_seen=5,
            total_commands=20,
            frames_executed=500,
            votes_processed=3,
        )
        async with TestClient(TestServer(_make_app(get_status=mock_uc))) as client:
            resp = await client.get("/api/status")
            assert resp.status == 200
            body = await resp.json()
            assert body["control_mode"] == "VOTING"

    async def test_returns_zero_counts_for_new_session(self) -> None:
        mock_uc = AsyncMock(spec=GetStatusUseCase)
        mock_uc.execute.return_value = StatusResponse(
            session_state=SessionState.RUNNING,
            control_mode=ControlMode.FIFO,
            connected_players=0,
            total_players_seen=0,
            total_commands=0,
            frames_executed=0,
            votes_processed=0,
        )
        async with TestClient(TestServer(_make_app(get_status=mock_uc))) as client:
            resp = await client.get("/api/status")
            assert resp.status == 200
            body = await resp.json()
            assert body["connected_players"] == 0
            assert body["total_commands"] == 0

    async def test_propagates_use_case_exception(self) -> None:
        mock_uc = AsyncMock(spec=GetStatusUseCase)
        mock_uc.execute.side_effect = ValueError("no session")
        async with TestClient(TestServer(_make_app(get_status=mock_uc))) as client:
            resp = await client.get("/api/status")
            assert resp.status == 400
            body = await resp.json()
            assert body["error"] == "no session"
