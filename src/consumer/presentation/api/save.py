from __future__ import annotations

from aiohttp import web  # type: ignore[import-untyped]

from consumer.application.dto.save import ManualSaveRequest
from consumer.application.use_cases.save_use_cases import ManualSaveUseCase


async def manual_save(request: web.Request) -> web.Response:
    use_case: ManualSaveUseCase = request.app["use_cases"]["manual_save"]
    response = await use_case.execute(ManualSaveRequest())
    return web.json_response(
        {
            "last_save_at": response.last_save_at.isoformat(),
            "save_count": response.save_count,
        }
    )


def register_save_routes(app: web.Application) -> None:
    app.router.add_post("/api/save", manual_save)
