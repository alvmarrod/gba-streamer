from datetime import timedelta

import pytest

from consumer.application.dto.administration import (
    ChangeControlModeRequest,
    ChangeControlModeResponse,
    ReloadConfigurationRequest,
    ReloadConfigurationResponse,
)
from consumer.domain.enums import ControlMode


class TestChangeControlModeDTOs:
    def test_request_construction(self) -> None:
        req = ChangeControlModeRequest(control_mode=ControlMode.VOTING)
        assert req.control_mode == ControlMode.VOTING

    def test_request_immutability(self) -> None:
        req = ChangeControlModeRequest(control_mode=ControlMode.VOTING)
        with pytest.raises(AttributeError):
            req.control_mode = ControlMode.FIFO  # type: ignore[misc]

    def test_response_construction(self) -> None:
        resp = ChangeControlModeResponse(control_mode=ControlMode.FIFO)
        assert resp.control_mode == ControlMode.FIFO


class TestReloadConfigurationDTOs:
    def test_request_construction(self) -> None:
        req = ReloadConfigurationRequest()
        assert req is not None

    def test_response_construction(self) -> None:
        resp = ReloadConfigurationResponse(
            control_mode=ControlMode.VOTING,
            voting_interval=timedelta(seconds=30),
            autosave_interval=timedelta(minutes=5),
        )
        assert resp.control_mode == ControlMode.VOTING
        assert resp.voting_interval == timedelta(seconds=30)
        assert resp.autosave_interval == timedelta(minutes=5)

    def test_response_immutability(self) -> None:
        resp = ReloadConfigurationResponse(
            control_mode=ControlMode.FIFO,
            voting_interval=timedelta(seconds=30),
            autosave_interval=timedelta(minutes=5),
        )
        with pytest.raises(AttributeError):
            resp.control_mode = ControlMode.VOTING  # type: ignore[misc]
