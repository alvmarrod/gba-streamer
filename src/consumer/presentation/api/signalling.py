from __future__ import annotations

from aiohttp import web  # type: ignore[import-untyped]
from aiortc import RTCPeerConnection, RTCSessionDescription  # type: ignore[import-untyped]

from consumer.infrastructure.streaming.aiortc_video_publisher import (
    AiortcVideoPublisher,
)


async def offer(request: web.Request) -> web.Response:
    publisher: AiortcVideoPublisher = request.app["publisher"]

    try:
        body = await request.json()
    except Exception:
        return web.json_response({"error": "Invalid JSON"}, status=400)

    if not isinstance(body, dict) or "sdp" not in body or "type" not in body:
        return web.json_response({"error": "Missing sdp or type"}, status=400)

    if body["type"] != "offer":
        return web.json_response({"error": "Expected offer"}, status=400)

    pc = RTCPeerConnection()
    publisher.add_peer(pc)

    try:
        offer_desc = RTCSessionDescription(sdp=body["sdp"], type=body["type"])
        await pc.setRemoteDescription(offer_desc)
        answer = await pc.createAnswer()
        await pc.setLocalDescription(answer)
    except Exception:
        await pc.close()
        return web.json_response({"error": "Invalid SDP"}, status=400)

    return web.json_response(
        {"sdp": pc.localDescription.sdp, "type": pc.localDescription.type}
    )


def register_signalling_routes(app: web.Application) -> None:
    app.router.add_post("/api/webrtc/offer", offer)
