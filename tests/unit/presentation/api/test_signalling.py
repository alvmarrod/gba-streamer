from __future__ import annotations

from unittest.mock import MagicMock

from aiohttp import web  # type: ignore[import-untyped]
from aiohttp.test_utils import TestClient, TestServer  # type: ignore[import-untyped]

from consumer.presentation.api.signalling import offer, register_signalling_routes


def _make_app(publisher: object | None = None) -> web.Application:
    app = web.Application()
    app["publisher"] = publisher
    app.router.add_post("/api/webrtc/offer", offer)
    return app


class TestOfferHandlerValidation:
    async def test_invalid_json(self) -> None:
        async with TestClient(TestServer(_make_app())) as client:
            resp = await client.post(
                "/api/webrtc/offer",
                data="not json",
                headers={"Content-Type": "application/json"},
            )
            assert resp.status == 400
            body = await resp.json()
            assert "error" in body

    async def test_missing_sdp(self) -> None:
        async with TestClient(TestServer(_make_app())) as client:
            resp = await client.post(
                "/api/webrtc/offer",
                json={"type": "offer"},
            )
            assert resp.status == 400
            body = await resp.json()
            assert body["error"] == "Missing sdp or type"

    async def test_missing_type(self) -> None:
        async with TestClient(TestServer(_make_app())) as client:
            resp = await client.post(
                "/api/webrtc/offer",
                json={"sdp": "something"},
            )
            assert resp.status == 400

    async def test_type_not_offer(self) -> None:
        async with TestClient(TestServer(_make_app())) as client:
            resp = await client.post(
                "/api/webrtc/offer",
                json={"sdp": "something", "type": "answer"},
            )
            assert resp.status == 400
            body = await resp.json()
            assert body["error"] == "Expected offer"

    async def test_non_dict_body(self) -> None:
        async with TestClient(TestServer(_make_app())) as client:
            resp = await client.post(
                "/api/webrtc/offer",
                json=[1, 2, 3],
            )
            assert resp.status == 400


class TestOfferHandlerRegistration:
    async def test_offer_calls_add_peer(self) -> None:
        mock_publisher = MagicMock()
        app = _make_app(mock_publisher)

        async with TestClient(TestServer(app)) as client:
            resp = await client.post(
                "/api/webrtc/offer",
                json={"sdp": "bad-sdp", "type": "offer"},
            )
            assert resp.status in (200, 400)
            mock_publisher.add_peer.assert_called_once()


class TestRegisterSignallingRoutes:
    def test_route_registered(self) -> None:
        app = web.Application()
        register_signalling_routes(app)
        routes = [r for r in app.router.routes()]
        assert len(routes) == 1
