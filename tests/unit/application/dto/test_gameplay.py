from uuid import uuid4

import pytest

from consumer.application.dto.gameplay import (
    ResolveInputRequest,
    ResolveInputResponse,
    SubmitInputRequest,
    SubmitInputResponse,
    TickEmulatorRequest,
    TickEmulatorResponse,
)
from consumer.domain.enums import Button


class TestSubmitInputDTOs:
    def test_request_construction(self) -> None:
        pid = uuid4()
        req = SubmitInputRequest(player_id=pid, button=Button.A)
        assert req.player_id == pid
        assert req.button == Button.A

    def test_request_immutability(self) -> None:
        req = SubmitInputRequest(player_id=uuid4(), button=Button.A)
        with pytest.raises(AttributeError):
            req.button = Button.B  # type: ignore[misc]

    def test_response_construction(self) -> None:
        resp = SubmitInputResponse()
        assert resp is not None


class TestResolveInputDTOs:
    def test_request_construction(self) -> None:
        req = ResolveInputRequest()
        assert req is not None

    def test_response_construction(self) -> None:
        resp = ResolveInputResponse()
        assert resp is not None


class TestTickEmulatorDTOs:
    def test_request_construction(self) -> None:
        req = TickEmulatorRequest()
        assert req is not None

    def test_response_construction(self) -> None:
        resp = TickEmulatorResponse()
        assert resp is not None
