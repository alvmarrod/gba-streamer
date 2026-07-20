from __future__ import annotations

from datetime import datetime, timedelta, timezone
from uuid import uuid4


from consumer.application.dto.administration import (
    ChangeControlModeRequest,
    ReloadConfigurationRequest,
)
from consumer.application.ports.configuration_provider_port import (
    ConfigurationProviderPort,
)
from consumer.application.ports.game_session_provider import GameSessionProvider
from consumer.application.use_cases.administration_use_cases import (
    ChangeControlModeUseCase,
    ReloadConfigurationUseCase,
)
from consumer.domain.entities.game_session import GameSession
from consumer.domain.enums import Button, ControlMode
from consumer.domain.value_objects import (
    GameInput,
    PlayerId,
    SessionConfiguration,
    SessionId,
)


def _make_session(
    control_mode: ControlMode = ControlMode.FIFO,
) -> GameSession:
    config = SessionConfiguration(
        control_mode=control_mode,
        voting_interval=timedelta(seconds=1),
        autosave_interval=timedelta(seconds=15),
    )
    return GameSession(
        session_id=SessionId(value=uuid4()),
        configuration=config,
    )


class StubSessionProvider(GameSessionProvider):
    def __init__(self, session: GameSession) -> None:
        self._session = session

    async def get_session(self) -> GameSession:
        return self._session


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
        session = _make_session(control_mode=ControlMode.FIFO)
        provider = StubSessionProvider(session)
        use_case = ChangeControlModeUseCase(provider)

        response = await use_case.execute(
            ChangeControlModeRequest(control_mode=ControlMode.VOTING)
        )

        assert response.control_mode == ControlMode.VOTING
        assert session.configuration.control_mode == ControlMode.VOTING

    async def test_change_to_fifo_clears_vote(self) -> None:
        session = _make_session(control_mode=ControlMode.VOTING)
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
        session = _make_session(control_mode=ControlMode.FIFO)
        provider = StubSessionProvider(session)
        use_case = ChangeControlModeUseCase(provider)

        response = await use_case.execute(
            ChangeControlModeRequest(control_mode=ControlMode.FIFO)
        )

        assert response.control_mode == ControlMode.FIFO


class TestReloadConfigurationUseCase:
    async def test_reload_updates_session_config(self) -> None:
        session = _make_session(control_mode=ControlMode.FIFO)
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
