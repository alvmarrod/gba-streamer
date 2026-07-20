from dataclasses import dataclass
from datetime import timedelta

from consumer.domain.enums import ControlMode


@dataclass(frozen=True)
class ChangeControlModeRequest:
    control_mode: ControlMode


@dataclass(frozen=True)
class ChangeControlModeResponse:
    control_mode: ControlMode


@dataclass(frozen=True)
class ReloadConfigurationRequest:
    pass


@dataclass(frozen=True)
class ReloadConfigurationResponse:
    control_mode: ControlMode
    voting_interval: timedelta
    autosave_interval: timedelta
