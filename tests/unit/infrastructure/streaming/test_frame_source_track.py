from __future__ import annotations

import asyncio

import av  # type: ignore[import-untyped]
import pytest

from consumer.infrastructure.streaming.frame_source_track import FrameSourceTrack


def _make_frame() -> av.VideoFrame:
    return av.VideoFrame(width=160, height=144, format="yuv420p")


class TestFrameSourceTrackRecv:
    async def test_recv_returns_pushed_frame(self) -> None:
        track = FrameSourceTrack()
        expected = _make_frame()
        track.push(expected)
        result = await track.recv()
        assert result is expected

    async def test_recv_waits_until_frame_pushed(self) -> None:
        track = FrameSourceTrack()
        received: list[av.VideoFrame] = []

        async def consumer() -> None:
            frame = await track.recv()
            received.append(frame)

        producer_task = asyncio.create_task(consumer())
        await asyncio.sleep(0.01)
        assert len(received) == 0

        frame = _make_frame()
        track.push(frame)
        await producer_task
        assert len(received) == 1
        assert received[0] is frame

    async def test_recv_returns_latest_frame(self) -> None:
        track = FrameSourceTrack()
        first = _make_frame()
        second = _make_frame()
        track.push(first)
        track.push(second)
        result = await track.recv()
        assert result is second

    async def test_recv_after_stop_raises(self) -> None:
        track = FrameSourceTrack()
        track.stop()
        with pytest.raises(Exception):
            await track.recv()


class TestFrameSourceTrackPush:
    async def test_push_sets_frame_event(self) -> None:
        track = FrameSourceTrack()
        assert not track._frame_event.is_set()
        frame = _make_frame()
        track.push(frame)
        assert track._frame_event.is_set()
        assert track._frame is frame
