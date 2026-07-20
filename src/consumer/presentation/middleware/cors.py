from __future__ import annotations

from typing import Awaitable, Callable

from aiohttp import web  # type: ignore[import-untyped]

_TELEGRAM_ORIGIN = "https://web.telegram.org"


@web.middleware
async def cors_middleware(
    request: web.Request,
    handler: Callable[[web.Request], Awaitable[web.StreamResponse]],
) -> web.StreamResponse:
    origin = request.headers.get("Origin")

    if not origin or origin != _TELEGRAM_ORIGIN:
        return await handler(request)

    if request.method == "OPTIONS":
        return _handle_preflight()

    response = await handler(request)
    _add_cors_headers(response)
    return response


def _handle_preflight() -> web.Response:
    response = web.Response(status=204)
    _add_cors_headers(response)
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type"
    response.headers["Access-Control-Max-Age"] = "86400"
    return response


def _add_cors_headers(response: web.StreamResponse) -> None:
    response.headers["Access-Control-Allow-Origin"] = _TELEGRAM_ORIGIN
    response.headers["Access-Control-Allow-Credentials"] = "true"
