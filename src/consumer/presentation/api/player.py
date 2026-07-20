from __future__ import annotations

from aiohttp import web  # type: ignore[import-untyped]

from consumer.application.dto.player import (
    ConnectPlayerRequest,
    DisconnectPlayerRequest,
)
from consumer.application.use_cases.player_use_cases import (
    ConnectPlayerUseCase,
    DisconnectPlayerUseCase,
)
from consumer.presentation.api.mappers import PresentationMapper


async def connect_player(request: web.Request) -> web.Response:
    use_case: ConnectPlayerUseCase = request.app["use_cases"]["connect_player"]
    body = PresentationMapper.require_str_dict(await request.json())

    player_id = PresentationMapper.to_uuid(
        PresentationMapper.to_str(body.get("player_id")), "player_id"
    )
    display_name = PresentationMapper.to_str(body.get("display_name"))

    dto = ConnectPlayerRequest(player_id=player_id, display_name=display_name)
    response = await use_case.execute(dto)
    return web.json_response(
        {
            "player_id": PresentationMapper.uuid_str(response.player_id),
            "display_name": response.display_name,
        },
        status=201,
    )


async def disconnect_player(request: web.Request) -> web.Response:
    use_case: DisconnectPlayerUseCase = request.app["use_cases"]["disconnect_player"]
    body = PresentationMapper.require_str_dict(await request.json())

    player_id = PresentationMapper.to_uuid(
        PresentationMapper.to_str(body.get("player_id")), "player_id"
    )

    dto = DisconnectPlayerRequest(player_id=player_id)
    await use_case.execute(dto)
    return web.json_response({}, status=200)


def register_player_routes(app: web.Application) -> None:
    app.router.add_post("/api/player/connect", connect_player)
    app.router.add_post("/api/player/disconnect", disconnect_player)
