from uuid import uuid4

import pytest

from consumer.application.dto.player import (
    ConnectPlayerRequest,
    ConnectPlayerResponse,
    DisconnectPlayerRequest,
    DisconnectPlayerResponse,
)


class TestConnectPlayerDTOs:
    def test_request_construction(self) -> None:
        pid = uuid4()
        req = ConnectPlayerRequest(player_id=pid, display_name="Alice")
        assert req.player_id == pid
        assert req.display_name == "Alice"

    def test_request_immutability(self) -> None:
        req = ConnectPlayerRequest(player_id=uuid4(), display_name="Alice")
        with pytest.raises(AttributeError):
            req.display_name = "Bob"  # type: ignore[misc]

    def test_response_construction(self) -> None:
        pid = uuid4()
        resp = ConnectPlayerResponse(player_id=pid, display_name="Alice")
        assert resp.player_id == pid
        assert resp.display_name == "Alice"


class TestDisconnectPlayerDTOs:
    def test_request_construction(self) -> None:
        pid = uuid4()
        req = DisconnectPlayerRequest(player_id=pid)
        assert req.player_id == pid

    def test_request_immutability(self) -> None:
        req = DisconnectPlayerRequest(player_id=uuid4())
        with pytest.raises(AttributeError):
            req.player_id = uuid4()  # type: ignore[misc]

    def test_response_construction(self) -> None:
        resp = DisconnectPlayerResponse()
        assert resp is not None
