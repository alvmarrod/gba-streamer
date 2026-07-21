from __future__ import annotations

import asyncio

import av  # type: ignore[import-untyped]
from aiortc.mediastreams import MediaStreamError, VideoStreamTrack  # type: ignore[import-untyped]


class FrameSourceTrack(VideoStreamTrack):
    kind = "video"

    def __init__(self) -> None:
        super().__init__()
        self._frame: av.VideoFrame | None = None
        self._frame_event = asyncio.Event()

    async def recv(self) -> av.VideoFrame:  # type: ignore[override]
        if self.readyState != "live":
            raise MediaStreamError
        while not self._frame_event.is_set():
            self._frame_event.clear()
            await self._frame_event.wait()
        self._frame_event.clear()
        assert self._frame is not None
        print(f"[recv] frame pts={self._frame.pts}", flush=True)
        return self._frame

    def push(self, frame: av.VideoFrame) -> None:
        self._frame = frame
        self._frame_event.set()
