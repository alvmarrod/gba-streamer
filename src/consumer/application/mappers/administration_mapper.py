from __future__ import annotations

from consumer.domain.enums import ControlMode
from consumer.domain.value_objects import SessionConfiguration

from consumer.application.dto.administration import (
    ChangeControlModeRequest,
    ReloadConfigurationResponse,
)


class AdministrationMapper:
    @staticmethod
    def to_control_mode(request: ChangeControlModeRequest) -> ControlMode:
        return request.control_mode

    @staticmethod
    def to_reload_response(config: SessionConfiguration) -> ReloadConfigurationResponse:
        return ReloadConfigurationResponse(
            control_mode=config.control_mode,
            voting_interval=config.voting_interval,
            autosave_interval=config.autosave_interval,
        )
