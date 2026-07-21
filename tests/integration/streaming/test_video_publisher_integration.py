from __future__ import annotations

import av  # type: ignore[import-untyped]
from aiortc import RTCPeerConnection  # type: ignore[import-untyped]

from consumer.application.ports.framebuffer_provider_port import (
    FramebufferProviderPort,
)
from consumer.infrastructure.streaming.aiortc_video_publisher import (
    AiortcVideoPublisher,
)

_RGBA_PIXELS = b"\x80\x90\xa0\xff" * (160 * 144)


class StubFramebufferProvider(FramebufferProviderPort):
    async def get_framebuffer(self) -> bytes:
        return _RGBA_PIXELS


class TestAiortcVideoPublisherIntegration:
    async def test_publish_with_real_peer_connection(self) -> None:
        provider = StubFramebufferProvider()
        publisher = AiortcVideoPublisher(provider)
        pc = RTCPeerConnection()
        publisher.add_peer(pc)

        assert pc in publisher._peer_connections

        await publisher.publish()
        frame = publisher._source_track._frame
        assert isinstance(frame, av.VideoFrame)
        assert frame.width == 160
        assert frame.height == 144

        await publisher.close()
        assert len(publisher._peer_connections) == 0

    async def test_publish_multiple_peers(self) -> None:
        provider = StubFramebufferProvider()
        publisher = AiortcVideoPublisher(provider)
        pc1 = RTCPeerConnection()
        pc2 = RTCPeerConnection()
        publisher.add_peer(pc1)
        publisher.add_peer(pc2)

        assert len(publisher._peer_connections) == 2

        await publisher.publish()
        assert publisher._source_track._frame is not None

        await publisher.close()
        assert len(publisher._peer_connections) == 0

    async def test_frame_converts_to_yuv420p(self) -> None:
        provider = StubFramebufferProvider()
        publisher = AiortcVideoPublisher(provider)
        await publisher.publish()

        frame = publisher._source_track._frame
        assert frame is not None
        assert frame.format is not None
        assert frame.format.name == "yuv420p"

    async def test_publish_logs_frame_info(self, caplog: object) -> None:
        import logging

        logger = logging.getLogger(
            "consumer.infrastructure.streaming.aiortc_video_publisher"
        )
        logger.setLevel(logging.DEBUG)
        caplog.set_level(logging.DEBUG)  # type: ignore[attr-defined]

        provider = StubFramebufferProvider()
        publisher = AiortcVideoPublisher(provider)
        await publisher.publish()
        caplog_text: str = caplog.text  # type: ignore[attr-defined]
        assert "frame_published" in caplog_text

    async def test_recv_does_not_crash(self) -> None:
        from consumer.infrastructure.streaming.frame_source_track import (
            FrameSourceTrack,
        )

        track = FrameSourceTrack()
        provider = StubFramebufferProvider()
        publisher = AiortcVideoPublisher(provider)
        await publisher.publish()
        track.push(publisher._source_track._frame)  # type: ignore[attr-defined, arg-type]

        async def _get_frame() -> None:
            await track.recv()

        await _get_frame()
