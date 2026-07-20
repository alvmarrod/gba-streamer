from __future__ import annotations

from pathlib import Path

from aiohttp import web  # type: ignore[import-untyped]

_WEBAPP_DIR = Path(__file__).parent
_STATIC_DIR = _WEBAPP_DIR / "static"


def get_index_html() -> str:
    return (_WEBAPP_DIR / "index.html").read_text()


async def index_handler(request: web.Request) -> web.Response:
    return web.Response(
        text=get_index_html(),
        content_type="text/html",
    )


def register_webapp_routes(app: web.Application) -> None:
    app.router.add_get("/", index_handler)
    app.router.add_static("/static", _STATIC_DIR)
