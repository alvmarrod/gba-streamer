import pytest

from consumer.application.ports.configuration_provider_port import (
    ConfigurationProviderPort,
)


class TestConfigurationProviderPort:
    def test_is_abstract(self) -> None:
        with pytest.raises(TypeError):
            ConfigurationProviderPort()  # type: ignore[abstract]

    def test_concrete_subclass(self) -> None:
        from datetime import timedelta

        from consumer.domain.enums import ControlMode
        from consumer.domain.value_objects import SessionConfiguration

        class Stub(ConfigurationProviderPort):
            async def load(self) -> SessionConfiguration:
                return SessionConfiguration(
                    control_mode=ControlMode.FIFO,
                    voting_interval=timedelta(seconds=30),
                    autosave_interval=timedelta(minutes=5),
                )

            async def reload(self) -> SessionConfiguration:
                return await self.load()

        port = Stub()
        assert port is not None
