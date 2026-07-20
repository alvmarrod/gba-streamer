from __future__ import annotations

from consumer.application.dto.administration import (
    ChangeControlModeRequest,
    ChangeControlModeResponse,
    ReloadConfigurationRequest,
    ReloadConfigurationResponse,
)
from consumer.application.mappers.administration_mapper import (
    AdministrationMapper,
)
from consumer.application.ports.configuration_provider_port import (
    ConfigurationProviderPort,
)
from consumer.application.ports.game_session_provider import GameSessionProvider


class ChangeControlModeUseCase:
    def __init__(self, session_provider: GameSessionProvider) -> None:
        self._session_provider = session_provider

    async def execute(
        self, request: ChangeControlModeRequest
    ) -> ChangeControlModeResponse:
        session = await self._session_provider.get_session()
        new_mode = AdministrationMapper.to_control_mode(request)
        session.change_control_mode(new_mode)
        return ChangeControlModeResponse(
            control_mode=session.configuration.control_mode
        )


class ReloadConfigurationUseCase:
    def __init__(
        self,
        session_provider: GameSessionProvider,
        configuration_provider: ConfigurationProviderPort,
    ) -> None:
        self._session_provider = session_provider
        self._configuration_provider = configuration_provider

    async def execute(
        self,
        request: ReloadConfigurationRequest,  # noqa: ARG002
    ) -> ReloadConfigurationResponse:
        session = await self._session_provider.get_session()
        config = await self._configuration_provider.reload()
        session.configure(config)
        return AdministrationMapper.to_reload_response(config)
