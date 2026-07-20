from __future__ import annotations

from aiohttp import web  # type: ignore[import-untyped]

from consumer.application.dto.gameplay import SubmitInputRequest
from consumer.application.use_cases.gameplay_use_cases import SubmitInputUseCase
from consumer.presentation.api.mappers import PresentationMapper


async def submit_input(request: web.Request) -> web.Response:
    use_case: SubmitInputUseCase = request.app["use_cases"]["submit_input"]
    body = PresentationMapper.require_str_dict(await request.json())

    player_id = PresentationMapper.to_uuid(
        PresentationMapper.to_str(body.get("player_id")), "player_id"
    )
    button = PresentationMapper.to_button(PresentationMapper.to_str(body.get("button")))

    dto = SubmitInputRequest(player_id=player_id, button=button)
    await use_case.execute(dto)
    return web.json_response({}, status=202)


def register_input_routes(app: web.Application) -> None:
    app.router.add_post("/api/input", submit_input)
