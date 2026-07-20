from __future__ import annotations

from datetime import datetime, timezone
from unittest.mock import AsyncMock

from aiohttp import web  # type: ignore[import-untyped]
from aiohttp.test_utils import TestClient, TestServer  # type: ignore[import-untyped]

from consumer.application.dto.save import ManualSaveResponse
from consumer.application.use_cases.save_use_cases import ManualSaveUseCase
from consumer.presentation.api.save import register_save_routes
from consumer.presentation.middleware.error_handler import error_handler_middleware


def _make_app(**use_cases: object) -> web.Application:
    app = web.Application()
    app.middlewares.append(error_handler_middleware)
    app["use_cases"] = use_cases
    register_save_routes(app)
    return app


class TestManualSave:
    async def test_returns_save_info(self) -> None:
        now = datetime(2026, 7, 20, 12, 0, 0, tzinfo=timezone.utc)
        mock_uc = AsyncMock(spec=ManualSaveUseCase)
        mock_uc.execute.return_value = ManualSaveResponse(
            last_save_at=now, save_count=5
        )
        async with TestClient(TestServer(_make_app(manual_save=mock_uc))) as client:
            resp = await client.post("/api/save")
            assert resp.status == 200
            body = await resp.json()
            assert body["last_save_at"] == "2026-07-20T12:00:00+00:00"
            assert body["save_count"] == 5

    async def test_calls_use_case_with_empty_request(self) -> None:
        from datetime import datetime, timezone

        mock_uc = AsyncMock(spec=ManualSaveUseCase)
        mock_uc.execute.return_value = ManualSaveResponse(
            last_save_at=datetime.now(tz=timezone.utc), save_count=1
        )
        async with TestClient(TestServer(_make_app(manual_save=mock_uc))) as client:
            await client.post("/api/save")
            call_args = mock_uc.execute.call_args[0][0]
            from consumer.application.dto.save import ManualSaveRequest

            assert isinstance(call_args, ManualSaveRequest)

    async def test_propagates_use_case_exception(self) -> None:
        mock_uc = AsyncMock(spec=ManualSaveUseCase)
        mock_uc.execute.side_effect = ValueError("disk full")
        async with TestClient(TestServer(_make_app(manual_save=mock_uc))) as client:
            resp = await client.post("/api/save")
            assert resp.status == 400
            body = await resp.json()
            assert body["error"] == "disk full"
