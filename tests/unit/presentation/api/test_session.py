from __future__ import annotations

from unittest.mock import AsyncMock

from aiohttp import web  # type: ignore[import-untyped]
from aiohttp.test_utils import TestClient, TestServer  # type: ignore[import-untyped]

from consumer.application.dto.monitoring import (
    HealthCheckResponse,
)
from consumer.application.dto.session import (
    StartSessionResponse,
    StopSessionResponse,
    PauseSessionResponse,
    ResumeSessionResponse,
)
from consumer.application.use_cases.monitoring_use_cases import HealthCheckUseCase
from consumer.application.use_cases.session_use_cases import (
    StartSessionUseCase,
    StopSessionUseCase,
    PauseSessionUseCase,
    ResumeSessionUseCase,
)
from consumer.domain.enums import SessionState
from consumer.presentation.api.session import register_session_routes
from consumer.presentation.middleware.error_handler import error_handler_middleware
from uuid import uuid4


def _make_app(**use_cases: object) -> web.Application:
    app = web.Application()
    app.middlewares.append(error_handler_middleware)
    app["use_cases"] = use_cases
    register_session_routes(app)
    return app


class TestGetSession:
    async def test_returns_session_info(self) -> None:
        mock_uc = AsyncMock(spec=HealthCheckUseCase)
        mock_uc.execute.return_value = HealthCheckResponse(
            session_state=SessionState.RUNNING,
            connected_players=2,
            is_healthy=True,
        )
        async with TestClient(TestServer(_make_app(health_check=mock_uc))) as client:
            resp = await client.get("/api/session")
            assert resp.status == 200
            body = await resp.json()
            assert body["session_state"] == "RUNNING"
            assert body["connected_players"] == 2
            assert body["is_healthy"] is True


class TestStartSession:
    async def test_returns_201_with_session_id(self) -> None:
        sid = uuid4()
        mock_uc = AsyncMock(spec=StartSessionUseCase)
        mock_uc.execute.return_value = StartSessionResponse(
            session_id=sid, state=SessionState.RUNNING
        )
        async with TestClient(TestServer(_make_app(start_session=mock_uc))) as client:
            resp = await client.post(
                "/api/session/start",
                json={
                    "control_mode": "fifo",
                    "voting_interval": 30,
                    "autosave_interval": 300,
                },
            )
            assert resp.status == 201
            body = await resp.json()
            assert body["session_id"] == str(sid)
            assert body["state"] == "RUNNING"

    async def test_missing_control_mode_returns_400(self) -> None:
        async with TestClient(
            TestServer(_make_app(start_session=AsyncMock()))
        ) as client:
            resp = await client.post("/api/session/start", json={})
            assert resp.status == 400

    async def test_invalid_control_mode_returns_400(self) -> None:
        async with TestClient(
            TestServer(_make_app(start_session=AsyncMock()))
        ) as client:
            resp = await client.post(
                "/api/session/start", json={"control_mode": "invalid"}
            )
            assert resp.status == 400

    async def test_defaults_intervals(self) -> None:
        mock_uc = AsyncMock(spec=StartSessionUseCase)
        mock_uc.execute.return_value = StartSessionResponse(
            session_id=uuid4(), state=SessionState.RUNNING
        )
        async with TestClient(TestServer(_make_app(start_session=mock_uc))) as client:
            resp = await client.post(
                "/api/session/start", json={"control_mode": "fifo"}
            )
            assert resp.status == 201
            call_args = mock_uc.execute.call_args[0][0]
            assert call_args.voting_interval.total_seconds() == 30
            assert call_args.autosave_interval.total_seconds() == 300


class TestStopSession:
    async def test_returns_state(self) -> None:
        mock_uc = AsyncMock(spec=StopSessionUseCase)
        mock_uc.execute.return_value = StopSessionResponse(state=SessionState.STOPPED)
        async with TestClient(TestServer(_make_app(stop_session=mock_uc))) as client:
            resp = await client.post("/api/session/stop")
            assert resp.status == 200
            body = await resp.json()
            assert body["state"] == "STOPPED"


class TestPauseSession:
    async def test_returns_state(self) -> None:
        mock_uc = AsyncMock(spec=PauseSessionUseCase)
        mock_uc.execute.return_value = PauseSessionResponse(state=SessionState.PAUSED)
        async with TestClient(TestServer(_make_app(pause_session=mock_uc))) as client:
            resp = await client.post("/api/session/pause")
            assert resp.status == 200
            body = await resp.json()
            assert body["state"] == "PAUSED"


class TestResumeSession:
    async def test_returns_state(self) -> None:
        mock_uc = AsyncMock(spec=ResumeSessionUseCase)
        mock_uc.execute.return_value = ResumeSessionResponse(state=SessionState.RUNNING)
        async with TestClient(TestServer(_make_app(resume_session=mock_uc))) as client:
            resp = await client.post("/api/session/resume")
            assert resp.status == 200
            body = await resp.json()
            assert body["state"] == "RUNNING"
