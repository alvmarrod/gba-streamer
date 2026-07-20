from __future__ import annotations

from datetime import timedelta
from uuid import uuid4


from consumer.application.dto.monitoring import (
    CollectMetricsRequest,
    HealthCheckRequest,
)
from consumer.application.ports.game_session_provider import GameSessionProvider
from consumer.application.ports.metrics_publisher_port import (
    MetricsPublisherPort,
)
from consumer.application.use_cases.monitoring_use_cases import (
    CollectMetricsUseCase,
    HealthCheckUseCase,
)
from consumer.domain.composed.vote_round import VoteRound
from consumer.domain.entities.game_session import GameSession
from consumer.domain.entities.player import Player
from consumer.domain.enums import ControlMode, SessionState
from consumer.domain.services.metrics_calculator import MetricsSnapshot
from consumer.domain.value_objects import (
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


class StubMetricsPublisher(MetricsPublisherPort):
    def __init__(self) -> None:
        self.published: MetricsSnapshot | None = None

    async def publish(self, metrics: MetricsSnapshot) -> None:
        self.published = metrics


class TestCollectMetricsUseCase:
    async def test_collect_metrics_publishes(self) -> None:
        session = _make_session()
        provider = StubSessionProvider(session)
        publisher = StubMetricsPublisher()
        use_case = CollectMetricsUseCase(provider, publisher)

        response = await use_case.execute(
            CollectMetricsRequest(),
            elapsed=timedelta(minutes=2),
        )

        assert publisher.published is not None
        assert response.counters.total_commands == 0
        assert response.counters.connected_players == 0
        assert response.commands_per_minute == 0.0
        assert response.active_player_ratio == 0.0

    async def test_collect_metrics_with_players(self) -> None:
        session = _make_session()
        session.connect_player(
            Player(player_id=PlayerId(value=uuid4()), display_name="Alice")
        )
        session.connect_player(
            Player(player_id=PlayerId(value=uuid4()), display_name="Bob")
        )
        provider = StubSessionProvider(session)
        publisher = StubMetricsPublisher()
        use_case = CollectMetricsUseCase(provider, publisher)

        response = await use_case.execute(
            CollectMetricsRequest(),
            elapsed=timedelta(minutes=1),
        )

        assert response.counters.connected_players == 2
        assert response.counters.total_players_seen == 2
        assert response.active_player_ratio == 1.0


class TestHealthCheckUseCase:
    async def test_healthy_session(self) -> None:
        session = _make_session()
        provider = StubSessionProvider(session)
        use_case = HealthCheckUseCase(provider)

        response = await use_case.execute(HealthCheckRequest())

        assert response.is_healthy is True
        assert response.session_state == SessionState.STARTING
        assert response.connected_players == 0

    async def test_unhealthy_player_count_mismatch(self) -> None:
        session = _make_session()
        session.metrics.increment_connected_players()
        provider = StubSessionProvider(session)
        use_case = HealthCheckUseCase(provider)

        response = await use_case.execute(HealthCheckRequest())

        assert response.is_healthy is False

    async def test_unhealthy_fifo_with_vote_round(self) -> None:
        session = _make_session(control_mode=ControlMode.FIFO)
        session.start()
        session._current_vote = VoteRound()
        provider = StubSessionProvider(session)
        use_case = HealthCheckUseCase(provider)

        response = await use_case.execute(HealthCheckRequest())

        assert response.is_healthy is False
