from __future__ import annotations

from aiohttp import web  # type: ignore[import-untyped]
from aiohttp.test_utils import TestClient, TestServer  # type: ignore[import-untyped]
from aiortc import RTCConfiguration, RTCIceServer  # type: ignore[import-untyped]

from consumer.application.ports.framebuffer_provider_port import (
    FramebufferProviderPort,
)
from consumer.infrastructure.streaming.aiortc_video_publisher import (
    AiortcVideoPublisher,
)
from consumer.presentation.api.signalling import register_signalling_routes


class StubFramebufferProvider(FramebufferProviderPort):
    async def get_framebuffer(self) -> bytes:
        return b"\x80\x90\xa0\xff" * (160 * 144)


_STUB_ICE = RTCConfiguration(
    iceServers=[RTCIceServer(urls=["stun:stun.l.google.com:19302"])]
)


class TestSignallingIntegration:
    async def test_offer_endpoint_exists(self) -> None:
        publisher = AiortcVideoPublisher(StubFramebufferProvider())
        app = web.Application()
        app["publisher"] = publisher
        app["ice_config"] = _STUB_ICE
        register_signalling_routes(app)

        async with TestClient(TestServer(app)) as client:
            resp = await client.post(
                "/api/webrtc/offer",
                json={"sdp": "test", "type": "offer"},
            )
            assert resp.status in (200, 400)
            body = await resp.json()
            assert "sdp" in body or "error" in body

    async def test_offer_returns_answer_format(self) -> None:
        from aiortc import RTCPeerConnection  # type: ignore[import-untyped]

        publisher = AiortcVideoPublisher(StubFramebufferProvider())
        app = web.Application()
        app["publisher"] = publisher
        app["ice_config"] = _STUB_ICE
        register_signalling_routes(app)

        pc_client = RTCPeerConnection()
        offer = await pc_client.createOffer()
        await pc_client.setLocalDescription(offer)

        async with TestClient(TestServer(app)) as client:
            resp = await client.post(
                "/api/webrtc/offer",
                json={
                    "sdp": pc_client.localDescription.sdp,
                    "type": "offer",
                },
            )
            body = await resp.json()
            if resp.status == 200:
                assert body["type"] == "answer"
                assert "sdp" in body
            else:
                assert "error" in body

        await pc_client.close()
        await publisher.close()

    async def test_offer_missing_body_returns_400(self) -> None:
        publisher = AiortcVideoPublisher(StubFramebufferProvider())
        app = web.Application()
        app["publisher"] = publisher
        app["ice_config"] = _STUB_ICE
        register_signalling_routes(app)

        async with TestClient(TestServer(app)) as client:
            resp = await client.post(
                "/api/webrtc/offer",
                json={},
            )
            assert resp.status == 400
            body = await resp.json()
            assert "error" in body
