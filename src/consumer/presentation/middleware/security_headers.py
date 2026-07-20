from __future__ import annotations

from typing import Awaitable, Callable

from aiohttp import web  # type: ignore[import-untyped]

_SECURITY_HEADERS: dict[str, str] = {
    "X-Content-Type-Options": "nosniff",
    "Referrer-Policy": "strict-origin-when-cross-origin",
    "X-Permitted-Cross-Domain-Policies": "none",
    "Permissions-Policy": "camera=(self), microphone=()",
}


@web.middleware
async def security_headers_middleware(
    request: web.Request,
    handler: Callable[[web.Request], Awaitable[web.StreamResponse]],
) -> web.StreamResponse:
    response = await handler(request)
    for key, value in _SECURITY_HEADERS.items():
        if key not in response.headers:
            response.headers[key] = value
    return response
