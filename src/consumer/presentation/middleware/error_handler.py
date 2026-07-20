from __future__ import annotations

from typing import Awaitable, Callable

from aiohttp import web  # type: ignore[import-untyped]

from consumer.domain.exceptions import (
    InvalidControlModeException,
    InvalidSessionStateException,
    PlayerAlreadyConnectedException,
    PlayerNotConnectedException,
    SessionNotRunningException,
    VoteAlreadyRunningException,
)

_ERROR_MAP: dict[type[Exception], int] = {
    ValueError: 400,
    InvalidControlModeException: 400,
    InvalidSessionStateException: 409,
    PlayerAlreadyConnectedException: 409,
    PlayerNotConnectedException: 404,
    SessionNotRunningException: 409,
    VoteAlreadyRunningException: 409,
}


@web.middleware
async def error_handler_middleware(
    request: web.Request,
    handler: Callable[[web.Request], Awaitable[web.StreamResponse]],
) -> web.StreamResponse:
    try:
        return await handler(request)
    except Exception as exc:
        status = 500
        message = "Internal server error"

        for exc_type, code in _ERROR_MAP.items():
            if isinstance(exc, exc_type):
                status = code
                message = str(exc)
                break

        return web.json_response({"error": message}, status=status)
