from __future__ import annotations

from aiohttp import web  # type: ignore[import-untyped]

from consumer.application.dto.session import (
    PauseSessionRequest,
    ResumeSessionRequest,
    StartSessionRequest,
    StopSessionRequest,
)
from consumer.application.use_cases.monitoring_use_cases import HealthCheckUseCase
from consumer.application.use_cases.session_use_cases import (
    PauseSessionUseCase,
    ResumeSessionUseCase,
    StartSessionUseCase,
    StopSessionUseCase,
)
from consumer.presentation.api.mappers import PresentationMapper


async def get_session(
    request: web.Request,
) -> web.Response:
    use_case: HealthCheckUseCase = request.app["use_cases"]["health_check"]
    from consumer.application.dto.monitoring import HealthCheckRequest

    response = await use_case.execute(HealthCheckRequest())
    return web.json_response(
        {
            "session_state": PresentationMapper.enum_name(response.session_state),
            "connected_players": response.connected_players,
            "is_healthy": response.is_healthy,
        }
    )


async def start_session(request: web.Request) -> web.Response:
    use_case: StartSessionUseCase = request.app["use_cases"]["start_session"]
    body = PresentationMapper.require_str_dict(await request.json())

    control_mode = PresentationMapper.to_control_mode(
        PresentationMapper.to_str(body.get("control_mode"))
    )
    voting_interval = PresentationMapper.to_timedelta_seconds(
        body.get("voting_interval", 30), "voting_interval"
    )
    autosave_interval = PresentationMapper.to_timedelta_seconds(
        body.get("autosave_interval", 300), "autosave_interval"
    )

    dto = StartSessionRequest(
        control_mode=control_mode,
        voting_interval=voting_interval,
        autosave_interval=autosave_interval,
    )
    response = await use_case.execute(dto)
    return web.json_response(
        {
            "session_id": PresentationMapper.uuid_str(response.session_id),
            "state": PresentationMapper.enum_name(response.state),
        },
        status=201,
    )


async def stop_session(request: web.Request) -> web.Response:
    use_case: StopSessionUseCase = request.app["use_cases"]["stop_session"]
    response = await use_case.execute(StopSessionRequest())
    return web.json_response({"state": PresentationMapper.enum_name(response.state)})


async def pause_session(request: web.Request) -> web.Response:
    use_case: PauseSessionUseCase = request.app["use_cases"]["pause_session"]
    response = await use_case.execute(PauseSessionRequest())
    return web.json_response({"state": PresentationMapper.enum_name(response.state)})


async def resume_session(request: web.Request) -> web.Response:
    use_case: ResumeSessionUseCase = request.app["use_cases"]["resume_session"]
    response = await use_case.execute(ResumeSessionRequest())
    return web.json_response({"state": PresentationMapper.enum_name(response.state)})


def register_session_routes(app: web.Application) -> None:
    app.router.add_get("/api/session", get_session)
    app.router.add_post("/api/session/start", start_session)
    app.router.add_post("/api/session/stop", stop_session)
    app.router.add_post("/api/session/pause", pause_session)
    app.router.add_post("/api/session/resume", resume_session)
