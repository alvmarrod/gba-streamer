from __future__ import annotations

import asyncio
import logging
from fractions import Fraction

import av  # type: ignore[import-untyped]
import numpy as np  # type: ignore[import-untyped]
from aiortc import RTCPeerConnection  # type: ignore[import-untyped]
from aiortc.contrib.media import MediaRelay  # type: ignore[import-untyped]

from consumer.application.ports.framebuffer_provider_port import (
    FramebufferProviderPort,
)
from consumer.application.ports.video_publisher_port import VideoPublisherPort
from consumer.infrastructure.streaming.frame_source_track import FrameSourceTrack

_log = logging.getLogger(__name__)


class AiortcVideoPublisher(VideoPublisherPort):
    def __init__(self, framebuffer_provider: FramebufferProviderPort) -> None:
        self._framebuffer_provider = framebuffer_provider
        self._source_track = FrameSourceTrack()
        self._relay = MediaRelay()
        self._peer_connections: set[RTCPeerConnection] = set()

    async def publish(self) -> None:
        raw = await self._framebuffer_provider.get_framebuffer()
        frame = self._convert(raw)
        self._source_track.push(frame)
        _log.debug("frame_published pts=%s", frame.pts)

    def add_peer(self, pc: RTCPeerConnection) -> None:
        self._peer_connections.add(pc)
        subscriber = self._relay.subscribe(self._source_track)
        pc.addTrack(subscriber)

        @pc.on("connectionstatechange")
        async def on_state_change() -> None:
            if pc.connectionState in ("failed", "closed", "disconnected"):
                self._peer_connections.discard(pc)

    async def close(self) -> None:
        coros = [pc.close() for pc in self._peer_connections]
        await asyncio.gather(*coros, return_exceptions=True)
        self._peer_connections.clear()

    @staticmethod
    def _convert(raw: bytes) -> av.VideoFrame:
        rgba = np.frombuffer(raw, dtype=np.uint8).reshape(144, 160, 4)
        frame = av.VideoFrame.from_ndarray(rgba, format="rgba")
        frame = frame.reformat(format="yuv420p")
        frame.pts = 0
        frame.time_base = Fraction(1, 90000)
        return frame
