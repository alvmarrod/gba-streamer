from __future__ import annotations

from datetime import datetime, timedelta, timezone
from uuid import uuid4


from tests.helpers.factories import make_session
from tests.helpers.stub_providers import StubSessionProvider

from consumer.application.dto.administration import (
    ChangeControlModeRequest,
    ReloadConfigurationRequest,
)
from consumer.application.ports.configuration_provider_port import (
    ConfigurationProviderPort,
)
from consumer.application.use_cases.administration_use_cases import (
    ChangeControlModeUseCase,
    ReloadConfigurationUseCase,
)
from consumer.domain.enums import Button, ControlMode
from consumer.domain.value_objects import (
    GameInput,
    PlayerId,
    SessionConfiguration,
)


class StubConfigurationProvider(ConfigurationProviderPort):
    def __init__(self, config: SessionConfiguration | None = None) -> None:
        self._config = config or SessionConfiguration(
            control_mode=ControlMode.VOTING,
            voting_interval=timedelta(seconds=30),
            autosave_interval=timedelta(minutes=5),
        )

    async def load(self) -> SessionConfiguration:
        return self._config

    async def reload(self) -> SessionConfiguration:
        return self._config


class TestChangeControlModeUseCase:
    async def test_change_to_voting(self) -> None:
        session = make_session(control_mode=ControlMode.FIFO)
        provider = StubSessionProvider(session)
        use_case = ChangeControlModeUseCase(provider)

        response = await use_case.execute(
            ChangeControlModeRequest(control_mode=ControlMode.VOTING)
        )

        assert response.control_mode == ControlMode.VOTING
        assert session.configuration.control_mode == ControlMode.VOTING

    async def test_change_to_fifo_clears_vote(self) -> None:
        session = make_session(control_mode=ControlMode.VOTING)
        session.start()
        pid = PlayerId(value=uuid4())
        session.submit_input(
            GameInput(
                button=Button.A,
                timestamp=datetime.now(tz=timezone.utc),
                player_id=pid,
            )
        )
        assert session.current_vote is not None

        provider = StubSessionProvider(session)
        use_case = ChangeControlModeUseCase(provider)

        response = await use_case.execute(
            ChangeControlModeRequest(control_mode=ControlMode.FIFO)
        )

        assert response.control_mode == ControlMode.FIFO
        assert session.current_vote is None

    async def test_change_to_same_mode_is_noop(self) -> None:
        session = make_session(control_mode=ControlMode.FIFO)
        provider = StubSessionProvider(session)
        use_case = ChangeControlModeUseCase(provider)

        response = await use_case.execute(
            ChangeControlModeRequest(control_mode=ControlMode.FIFO)
        )

        assert response.control_mode == ControlMode.FIFO


class TestReloadConfigurationUseCase:
    async def test_reload_updates_session_config(self) -> None:
        session = make_session(control_mode=ControlMode.FIFO)
        provider = StubSessionProvider(session)
        new_config = SessionConfiguration(
            control_mode=ControlMode.VOTING,
            voting_interval=timedelta(seconds=30),
            autosave_interval=timedelta(minutes=5),
        )
        config_provider = StubConfigurationProvider(config=new_config)
        use_case = ReloadConfigurationUseCase(provider, config_provider)

        response = await use_case.execute(ReloadConfigurationRequest())

        assert response.control_mode == ControlMode.VOTING
        assert response.voting_interval == timedelta(seconds=30)
        assert session.configuration.control_mode == ControlMode.VOTING
