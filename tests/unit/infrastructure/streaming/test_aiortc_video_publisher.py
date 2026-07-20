from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import av  # type: ignore[import-untyped]

from consumer.infrastructure.streaming.aiortc_video_publisher import (
    AiortcVideoPublisher,
)

_RGBA_PIXELS = b"\x80\x90\xa0\xff" * (160 * 144)


def _mock_framebuffer_provider() -> AsyncMock:
    provider = AsyncMock()
    provider.get_framebuffer.return_value = _RGBA_PIXELS
    return provider


def _mock_pc() -> MagicMock:
    pc = MagicMock()
    pc.connectionState = "new"
    pc.addTrack = MagicMock()
    pc.on = MagicMock(return_value=MagicMock())
    pc.close = AsyncMock()
    return pc


class TestAiortcVideoPublish:
    async def test_publish_calls_framebuffer_provider(self) -> None:
        provider = _mock_framebuffer_provider()
        publisher = AiortcVideoPublisher(provider)
        await publisher.publish()
        provider.get_framebuffer.assert_awaited_once()

    async def test_publish_pushes_frame_to_track(self) -> None:
        provider = _mock_framebuffer_provider()
        publisher = AiortcVideoPublisher(provider)
        await publisher.publish()
        assert publisher._source_track._frame is not None
        assert isinstance(publisher._source_track._frame, av.VideoFrame)

    async def test_publish_without_peers_does_not_raise(self) -> None:
        provider = _mock_framebuffer_provider()
        publisher = AiortcVideoPublisher(provider)
        await publisher.publish()


class TestAiortcVideoConvert:
    def test_convert_rgba_to_yuv420p(self) -> None:
        frame = AiortcVideoPublisher._convert(_RGBA_PIXELS)
        assert isinstance(frame, av.VideoFrame)
        assert frame.width == 160
        assert frame.height == 144
        assert frame.format.name == "yuv420p"

    def test_convert_dimensions(self) -> None:
        raw = b"\x00" * (160 * 144 * 4)
        frame = AiortcVideoPublisher._convert(raw)
        assert frame.width == 160
        assert frame.height == 144


class TestAiortcVideoPublisherAddPeer:
    async def test_add_peer_adds_track(self) -> None:
        provider = _mock_framebuffer_provider()
        publisher = AiortcVideoPublisher(provider)
        pc = _mock_pc()
        publisher.add_peer(pc)
        pc.addTrack.assert_called_once()

    async def test_add_peer_registers_state_handler(self) -> None:
        provider = _mock_framebuffer_provider()
        publisher = AiortcVideoPublisher(provider)
        pc = _mock_pc()
        publisher.add_peer(pc)
        pc.on.assert_called_once()
        args = pc.on.call_args
        assert args[0][0] == "connectionstatechange"

    async def test_add_peer_tracks_connection(self) -> None:
        provider = _mock_framebuffer_provider()
        publisher = AiortcVideoPublisher(provider)
        pc = _mock_pc()
        publisher.add_peer(pc)
        assert pc in publisher._peer_connections

    async def test_multiple_peers(self) -> None:
        provider = _mock_framebuffer_provider()
        publisher = AiortcVideoPublisher(provider)
        pc1, pc2 = _mock_pc(), _mock_pc()
        publisher.add_peer(pc1)
        publisher.add_peer(pc2)
        assert len(publisher._peer_connections) == 2


class TestAiortcVideoPublisherClose:
    async def test_close_closes_all_peer_connections(self) -> None:
        provider = _mock_framebuffer_provider()
        publisher = AiortcVideoPublisher(provider)
        pc1, pc2 = _mock_pc(), _mock_pc()
        publisher.add_peer(pc1)
        publisher.add_peer(pc2)
        await publisher.close()
        pc1.close.assert_awaited_once()
        pc2.close.assert_awaited_once()
        assert len(publisher._peer_connections) == 0

    async def test_close_empty_set(self) -> None:
        provider = _mock_framebuffer_provider()
        publisher = AiortcVideoPublisher(provider)
        await publisher.close()
