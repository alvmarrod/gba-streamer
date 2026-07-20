from __future__ import annotations

from unittest.mock import AsyncMock
from uuid import uuid4

from aiohttp import web  # type: ignore[import-untyped]
from aiohttp.test_utils import TestClient, TestServer  # type: ignore[import-untyped]

from consumer.application.dto.gameplay import SubmitInputResponse
from consumer.application.use_cases.gameplay_use_cases import SubmitInputUseCase
from consumer.presentation.api.input import register_input_routes
from consumer.presentation.middleware.error_handler import error_handler_middleware


def _make_app(**use_cases: object) -> web.Application:
    app = web.Application()
    app.middlewares.append(error_handler_middleware)
    app["use_cases"] = use_cases
    register_input_routes(app)
    return app


class TestSubmitInput:
    async def test_returns_202(self) -> None:
        mock_uc = AsyncMock(spec=SubmitInputUseCase)
        mock_uc.execute.return_value = SubmitInputResponse()
        async with TestClient(TestServer(_make_app(submit_input=mock_uc))) as client:
            resp = await client.post(
                "/api/input",
                json={"player_id": str(uuid4()), "button": "a"},
            )
            assert resp.status == 202
            body = await resp.json()
            assert body == {}

    async def test_missing_player_id_returns_400(self) -> None:
        async with TestClient(
            TestServer(_make_app(submit_input=AsyncMock()))
        ) as client:
            resp = await client.post("/api/input", json={"button": "a"})
            assert resp.status == 400

    async def test_missing_button_returns_400(self) -> None:
        async with TestClient(
            TestServer(_make_app(submit_input=AsyncMock()))
        ) as client:
            resp = await client.post("/api/input", json={"player_id": str(uuid4())})
            assert resp.status == 400

    async def test_invalid_button_returns_400(self) -> None:
        async with TestClient(
            TestServer(_make_app(submit_input=AsyncMock()))
        ) as client:
            resp = await client.post(
                "/api/input",
                json={"player_id": str(uuid4()), "button": "invalid"},
            )
            assert resp.status == 400

    async def test_all_valid_buttons(self) -> None:
        for button in ["up", "down", "left", "right", "a", "b", "start", "select"]:
            mock_uc = AsyncMock(spec=SubmitInputUseCase)
            mock_uc.execute.return_value = SubmitInputResponse()
            async with TestClient(
                TestServer(_make_app(submit_input=mock_uc))
            ) as client:
                resp = await client.post(
                    "/api/input",
                    json={"player_id": str(uuid4()), "button": button},
                )
                assert resp.status == 202, f"Button {button} failed"
