from __future__ import annotations

from datetime import timedelta
from unittest.mock import AsyncMock

from aiohttp import web  # type: ignore[import-untyped]
from aiohttp.test_utils import TestClient, TestServer  # type: ignore[import-untyped]

from consumer.application.dto.administration import (
    ChangeControlModeResponse,
    ReloadConfigurationResponse,
)
from consumer.application.use_cases.administration_use_cases import (
    ChangeControlModeUseCase,
    ReloadConfigurationUseCase,
)
from consumer.domain.enums import ControlMode
from consumer.presentation.api.admin import register_admin_routes
from consumer.presentation.middleware.error_handler import error_handler_middleware


def _make_app(**use_cases: object) -> web.Application:
    app = web.Application()
    app.middlewares.append(error_handler_middleware)
    app["use_cases"] = use_cases
    register_admin_routes(app)
    return app


class TestChangeControlMode:
    async def test_returns_mode(self) -> None:
        mock_uc = AsyncMock(spec=ChangeControlModeUseCase)
        mock_uc.execute.return_value = ChangeControlModeResponse(
            control_mode=ControlMode.VOTING
        )
        async with TestClient(
            TestServer(_make_app(change_control_mode=mock_uc))
        ) as client:
            resp = await client.post(
                "/api/control-mode", json={"control_mode": "voting"}
            )
            assert resp.status == 200
            body = await resp.json()
            assert body["control_mode"] == "VOTING"

    async def test_invalid_mode_returns_400(self) -> None:
        async with TestClient(
            TestServer(_make_app(change_control_mode=AsyncMock()))
        ) as client:
            resp = await client.post(
                "/api/control-mode", json={"control_mode": "invalid"}
            )
            assert resp.status == 400

    async def test_missing_mode_returns_400(self) -> None:
        async with TestClient(
            TestServer(_make_app(change_control_mode=AsyncMock()))
        ) as client:
            resp = await client.post("/api/control-mode", json={})
            assert resp.status == 400


class TestReloadConfiguration:
    async def test_returns_config(self) -> None:
        mock_uc = AsyncMock(spec=ReloadConfigurationUseCase)
        mock_uc.execute.return_value = ReloadConfigurationResponse(
            control_mode=ControlMode.FIFO,
            voting_interval=timedelta(seconds=30),
            autosave_interval=timedelta(seconds=300),
        )
        async with TestClient(
            TestServer(_make_app(reload_configuration=mock_uc))
        ) as client:
            resp = await client.post("/api/config/reload")
            assert resp.status == 200
            body = await resp.json()
            assert body["control_mode"] == "FIFO"
            assert body["voting_interval"] == 30.0
            assert body["autosave_interval"] == 300.0
