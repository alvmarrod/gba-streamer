from __future__ import annotations

from uuid import uuid4


from consumer.application.dto.voting import ResolveVoteRequest
from consumer.application.use_cases.voting_use_cases import (
    ResolveVoteUseCase,
)
from consumer.domain.enums import Button, ControlMode
from consumer.domain.value_objects import PlayerId

from tests.helpers.factories import make_game_input, make_session
from tests.helpers.stub_providers import StubSessionProvider


class TestResolveVoteUseCase:
    async def test_resolve_vote_clears_round(self) -> None:
        session = make_session(control_mode=ControlMode.VOTING)
        session.start()
        pid = PlayerId(value=uuid4())
        gi = make_game_input(Button.A, pid)
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
        session = make_session(control_mode=ControlMode.VOTING)
        session.start()
        assert session.current_vote is None

        provider = StubSessionProvider(session)
        use_case = ResolveVoteUseCase(provider)

        response = await use_case.execute(ResolveVoteRequest())

        assert response.vote_count == 0

    async def test_resolve_vote_majority_wins(self) -> None:
        session = make_session(control_mode=ControlMode.VOTING)
        session.start()
        pid1 = PlayerId(value=uuid4())
        pid2 = PlayerId(value=uuid4())
        pid3 = PlayerId(value=uuid4())
        session.submit_input(make_game_input(Button.LEFT, pid1))
        session.submit_input(make_game_input(Button.LEFT, pid2))
        session.submit_input(make_game_input(Button.RIGHT, pid3))

        provider = StubSessionProvider(session)
        use_case = ResolveVoteUseCase(provider)

        response = await use_case.execute(ResolveVoteRequest())

        assert response.winning_button == Button.LEFT
        assert response.vote_count == 2
        assert session.metrics.votes_processed == 1
