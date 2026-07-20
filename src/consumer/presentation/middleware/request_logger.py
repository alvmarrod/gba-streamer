from __future__ import annotations

import time
from typing import Awaitable, Callable

from aiohttp import web  # type: ignore[import-untyped]

from consumer.application.ports.logger_port import LoggerPort


def request_logger_middleware(
    logger: LoggerPort,
) -> Callable[
    [web.Request, Callable[[web.Request], Awaitable[web.StreamResponse]]],
    Awaitable[web.StreamResponse],
]:
    @web.middleware
    async def middleware(
        request: web.Request,
        handler: Callable[[web.Request], Awaitable[web.StreamResponse]],
    ) -> web.StreamResponse:
        start = time.monotonic()
        try:
            response = await handler(request)
        except Exception:
            duration_ms = (time.monotonic() - start) * 1000
            await logger.error(
                "request_failed",
                method=request.method,
                path=request.path,
                duration_ms=round(duration_ms, 2),
            )
            raise

        duration_ms = (time.monotonic() - start) * 1000
        await logger.info(
            "request_completed",
            method=request.method,
            path=request.path,
            status=response.status,
            duration_ms=round(duration_ms, 2),
        )
        return response

    return middleware
