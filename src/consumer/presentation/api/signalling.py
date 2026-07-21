from __future__ import annotations

import logging

from aiohttp import web  # type: ignore[import-untyped]
from aiortc import (
    RTCConfiguration,
    RTCPeerConnection,
    RTCSessionDescription,
)  # type: ignore[import-untyped]

from consumer.infrastructure.streaming.aiortc_video_publisher import (
    AiortcVideoPublisher,
)

_log = logging.getLogger(__name__)


async def offer(request: web.Request) -> web.Response:
    publisher: AiortcVideoPublisher = request.app["publisher"]
    ice_config: RTCConfiguration = request.app["ice_config"]

    try:
        body = await request.json()
    except Exception:
        return web.json_response({"error": "Invalid JSON"}, status=400)

    if not isinstance(body, dict) or "sdp" not in body or "type" not in body:
        return web.json_response({"error": "Missing sdp or type"}, status=400)

    if body["type"] != "offer":
        return web.json_response({"error": "Expected offer"}, status=400)

    from aiortc import RTCConfiguration as _RTCConfiguration  # type: ignore[import-untyped]

    turn_servers = [
        s for s in (ice_config.iceServers or []) if any("turn:" in u for u in s.urls)
    ]
    if turn_servers:
        ice_config = _RTCConfiguration(iceServers=turn_servers)
    pc = RTCPeerConnection(configuration=ice_config)
    _log.info("ice_servers_count=%d", len(ice_config.iceServers or []))

    @pc.on("iceconnectionstatechange")
    async def _on_ice_change() -> None:
        _log.info("ice_state=%s", pc.iceConnectionState)

    @pc.on("icegatheringstatechange")
    async def _on_gathering_change() -> None:
        _log.info("ice_gathering=%s", pc.iceGatheringState)

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
