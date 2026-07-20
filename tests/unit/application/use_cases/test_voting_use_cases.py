from __future__ import annotations

from datetime import datetime, timedelta, timezone
from uuid import uuid4


from consumer.application.dto.voting import ResolveVoteRequest
from consumer.application.ports.game_session_provider import GameSessionProvider
from consumer.application.use_cases.voting_use_cases import (
    ResolveVoteUseCase,
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
    control_mode: ControlMode = ControlMode.VOTING,
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


def _make_game_input(
    button: Button = Button.A, player_id: PlayerId | None = None
) -> GameInput:
    return GameInput(
        button=button,
        timestamp=datetime.now(tz=timezone.utc),
        player_id=player_id or PlayerId(value=uuid4()),
    )


class StubSessionProvider(GameSessionProvider):
    def __init__(self, session: GameSession) -> None:
        self._session = session

    async def get_session(self) -> GameSession:
        return self._session


class TestResolveVoteUseCase:
    async def test_resolve_vote_clears_round(self) -> None:
        session = _make_session()
        session.start()
        pid = PlayerId(value=uuid4())
        gi = _make_game_input(Button.A, pid)
        session.submit_input(gi)
        assert session.current_vote is not None

        provider = StubSessionProvider(session)
        use_case = ResolveVoteUseCase(provider)

        response = await use_case.execute(ResolveVoteRequest())

        assert response.winning_button == Button.A
        assert response.vote_count == 1
        assert session.current_vote is None
        assert session.metrics.votes_processed == 1

    async def test_resolve_vote_no_vote_round(self) -> None:
        session = _make_session()
        session.start()
        assert session.current_vote is None

        provider = StubSessionProvider(session)
        use_case = ResolveVoteUseCase(provider)

        response = await use_case.execute(ResolveVoteRequest())

        assert response.vote_count == 0

    async def test_resolve_vote_majority_wins(self) -> None:
        session = _make_session()
        session.start()
        pid1 = PlayerId(value=uuid4())
        pid2 = PlayerId(value=uuid4())
        pid3 = PlayerId(value=uuid4())
        session.submit_input(_make_game_input(Button.LEFT, pid1))
        session.submit_input(_make_game_input(Button.LEFT, pid2))
        session.submit_input(_make_game_input(Button.RIGHT, pid3))

        provider = StubSessionProvider(session)
        use_case = ResolveVoteUseCase(provider)

        response = await use_case.execute(ResolveVoteRequest())

        assert response.winning_button == Button.LEFT
        assert response.vote_count == 2
        assert session.metrics.votes_processed == 1
