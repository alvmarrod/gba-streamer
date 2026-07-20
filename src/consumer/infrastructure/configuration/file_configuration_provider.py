from __future__ import annotations

import asyncio
from datetime import timedelta
from pathlib import Path

import yaml

from consumer.application.ports.configuration_provider_port import (
    ConfigurationProviderPort,
)
from consumer.domain.enums import ControlMode
from consumer.domain.value_objects import SessionConfiguration

_DEFAULT_CONTROL_MODE = ControlMode.FIFO
_DEFAULT_VOTING_INTERVAL = timedelta(seconds=30)
_DEFAULT_AUTOSAVE_INTERVAL = timedelta(seconds=15)


class FileConfigurationProvider(ConfigurationProviderPort):
    def __init__(self, config_path: Path) -> None:
        self._config_path = config_path

    async def load(self) -> SessionConfiguration:
        return await asyncio.to_thread(self._load_sync)

    async def reload(self) -> SessionConfiguration:
        return await asyncio.to_thread(self._load_sync)

    def _load_sync(self) -> SessionConfiguration:
        if not self._config_path.exists():
            raise FileNotFoundError(
                f"Configuration file not found: {self._config_path}"
            )

        with self._config_path.open() as f:
            raw = yaml.safe_load(f)

        if raw is None:
            return SessionConfiguration(
                control_mode=_DEFAULT_CONTROL_MODE,
                voting_interval=_DEFAULT_VOTING_INTERVAL,
                autosave_interval=_DEFAULT_AUTOSAVE_INTERVAL,
            )

        if not isinstance(raw, dict):
            raise ValueError(f"Expected YAML mapping, got {type(raw).__name__}")

        control_mode_str = raw.get("control_mode", "FIFO")
        try:
            control_mode = ControlMode[control_mode_str.upper()]
        except KeyError:
            raise ValueError(f"Invalid control_mode: {control_mode_str!r}") from None

        voting_seconds = raw.get("voting_interval", 30)
        autosave_seconds = raw.get("autosave_interval", 15)

        return SessionConfiguration(
            control_mode=control_mode,
            voting_interval=timedelta(seconds=float(voting_seconds)),
            autosave_interval=timedelta(seconds=float(autosave_seconds)),
        )
