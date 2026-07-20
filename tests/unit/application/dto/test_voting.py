import pytest

from consumer.application.dto.voting import (
    ResolveVoteRequest,
    ResolveVoteResponse,
)
from consumer.domain.enums import Button


class TestResolveVoteDTOs:
    def test_request_construction(self) -> None:
        req = ResolveVoteRequest()
        assert req is not None

    def test_response_construction(self) -> None:
        resp = ResolveVoteResponse(winning_button=Button.UP, vote_count=5)
        assert resp.winning_button == Button.UP
        assert resp.vote_count == 5

    def test_response_immutability(self) -> None:
        resp = ResolveVoteResponse(winning_button=Button.UP, vote_count=5)
        with pytest.raises(AttributeError):
            resp.vote_count = 10  # type: ignore[misc]
