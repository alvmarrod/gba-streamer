from __future__ import annotations

import time
from typing import Awaitable, Callable

from aiohttp import web  # type: ignore[import-untyped]

from consumer.application.ports.logger_port import LoggerPort

_QUIET_PATHS: set[str] = {"/api/session", "/api/status", "/api/health"}


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
        quiet = request.path in _QUIET_PATHS and response.status < 400
        log_method = logger.debug if quiet else logger.info
        await log_method(
            "request_completed",
            method=request.method,
            path=request.path,
            status=response.status,
            duration_ms=round(duration_ms, 2),
        )
        return response

    return middleware
