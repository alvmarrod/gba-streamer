from datetime import timedelta

from consumer.application.dto.administration import ChangeControlModeRequest
from consumer.application.mappers.administration_mapper import AdministrationMapper
from consumer.domain.enums import ControlMode
from consumer.domain.value_objects import SessionConfiguration


class TestAdministrationMapper:
    def test_to_control_mode(self) -> None:
        req = ChangeControlModeRequest(control_mode=ControlMode.VOTING)
        mode = AdministrationMapper.to_control_mode(req)
        assert mode == ControlMode.VOTING

    def test_to_reload_response(self) -> None:
        config = SessionConfiguration(
            control_mode=ControlMode.FIFO,
            voting_interval=timedelta(seconds=30),
            autosave_interval=timedelta(minutes=5),
        )
        resp = AdministrationMapper.to_reload_response(config)

        assert resp.control_mode == ControlMode.FIFO
        assert resp.voting_interval == timedelta(seconds=30)
        assert resp.autosave_interval == timedelta(minutes=5)
