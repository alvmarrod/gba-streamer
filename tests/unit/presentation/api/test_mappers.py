from __future__ import annotations

import pytest

from consumer.domain.enums import Button, ControlMode, SessionState
from consumer.presentation.api.mappers import PresentationMapper


class TestToUuid:
    def test_valid_uuid(self) -> None:
        result = PresentationMapper.to_uuid("550e8400-e29b-41d4-a716-446655440000")
        assert str(result) == "550e8400-e29b-41d4-a716-446655440000"

    def test_invalid_uuid_raises(self) -> None:
        with pytest.raises(ValueError, match="Invalid player_id"):
            PresentationMapper.to_uuid("not-a-uuid", "player_id")


class TestToControlMode:
    def test_fifo(self) -> None:
        assert PresentationMapper.to_control_mode("fifo") == ControlMode.FIFO

    def test_voting(self) -> None:
        assert PresentationMapper.to_control_mode("voting") == ControlMode.VOTING

    def test_case_insensitive(self) -> None:
        assert PresentationMapper.to_control_mode("FIFO") == ControlMode.FIFO

    def test_invalid_raises(self) -> None:
        with pytest.raises(ValueError, match="Invalid control_mode"):
            PresentationMapper.to_control_mode("invalid")


class TestToButton:
    def test_all_buttons(self) -> None:
        for name in ["up", "down", "left", "right", "a", "b", "start", "select"]:
            assert PresentationMapper.to_button(name) == Button[name.upper()]

    def test_invalid_raises(self) -> None:
        with pytest.raises(ValueError, match="Invalid button"):
            PresentationMapper.to_button("invalid")


class TestToSessionState:
    def test_valid_states(self) -> None:
        for name in ["starting", "running", "paused", "stopping", "stopped"]:
            assert (
                PresentationMapper.to_session_state(name) == SessionState[name.upper()]
            )

    def test_invalid_raises(self) -> None:
        with pytest.raises(ValueError, match="Invalid session_state"):
            PresentationMapper.to_session_state("invalid")


class TestToTimedeltaSeconds:
    def test_int(self) -> None:
        result = PresentationMapper.to_timedelta_seconds(30)
        assert result.total_seconds() == 30.0

    def test_float(self) -> None:
        result = PresentationMapper.to_timedelta_seconds(1.5)
        assert result.total_seconds() == 1.5

    def test_invalid_type_raises(self) -> None:
        with pytest.raises(ValueError, match="expected seconds"):
            PresentationMapper.to_timedelta_seconds("30")


class TestToStr:
    def test_string(self) -> None:
        assert PresentationMapper.to_str("hello") == "hello"

    def test_none_raises(self) -> None:
        with pytest.raises(ValueError, match="Value is required"):
            PresentationMapper.to_str(None)


class TestRequireStrDict:
    def test_valid(self) -> None:
        result = PresentationMapper.require_str_dict({"a": 1})
        assert result == {"a": 1}

    def test_invalid_raises(self) -> None:
        with pytest.raises(ValueError, match="expected JSON object"):
            PresentationMapper.require_str_dict([1, 2])


class TestEnumName:
    def test_enum(self) -> None:
        assert PresentationMapper.enum_name(ControlMode.FIFO) == "FIFO"

    def test_non_enum(self) -> None:
        assert PresentationMapper.enum_name("string") == "string"


class TestTimedeltaSeconds:
    def test_conversion(self) -> None:
        from datetime import timedelta

        assert PresentationMapper.timedelta_seconds(timedelta(seconds=30)) == 30.0
