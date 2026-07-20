from __future__ import annotations

from aiohttp import web  # type: ignore[import-untyped]

from consumer.application.dto.administration import (
    ChangeControlModeRequest,
    ReloadConfigurationRequest,
)
from consumer.application.use_cases.administration_use_cases import (
    ChangeControlModeUseCase,
    ReloadConfigurationUseCase,
)
from consumer.presentation.api.mappers import PresentationMapper


async def change_control_mode(request: web.Request) -> web.Response:
    use_case: ChangeControlModeUseCase = request.app["use_cases"]["change_control_mode"]
    body = PresentationMapper.require_str_dict(await request.json())

    control_mode = PresentationMapper.to_control_mode(
        PresentationMapper.to_str(body.get("control_mode"))
    )

    dto = ChangeControlModeRequest(control_mode=control_mode)
    response = await use_case.execute(dto)
    return web.json_response(
        {"control_mode": PresentationMapper.enum_name(response.control_mode)}
    )


async def reload_configuration(request: web.Request) -> web.Response:
    use_case: ReloadConfigurationUseCase = request.app["use_cases"][
        "reload_configuration"
    ]
    response = await use_case.execute(ReloadConfigurationRequest())
    return web.json_response(
        {
            "control_mode": PresentationMapper.enum_name(response.control_mode),
            "voting_interval": PresentationMapper.timedelta_seconds(
                response.voting_interval
            ),
            "autosave_interval": PresentationMapper.timedelta_seconds(
                response.autosave_interval
            ),
        }
    )


def register_admin_routes(app: web.Application) -> None:
    app.router.add_post("/api/control-mode", change_control_mode)
    app.router.add_post("/api/config/reload", reload_configuration)
