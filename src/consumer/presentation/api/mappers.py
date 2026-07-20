from __future__ import annotations

from datetime import timedelta
from uuid import UUID

from consumer.domain.enums import Button, ControlMode, SessionState


class PresentationMapper:
    @staticmethod
    def to_uuid(value: str, field: str = "id") -> UUID:
        try:
            return UUID(value)
        except (ValueError, AttributeError) as exc:
            raise ValueError(f"Invalid {field}: {value}") from exc

    @staticmethod
    def to_control_mode(value: str) -> ControlMode:
        try:
            return ControlMode[value.upper()]
        except KeyError as exc:
            valid = [m.name.lower() for m in ControlMode]
            raise ValueError(
                f"Invalid control_mode: {value}. Must be one of: {valid}"
            ) from exc

    @staticmethod
    def to_button(value: str) -> Button:
        try:
            return Button[value.upper()]
        except KeyError as exc:
            valid = [b.name.lower() for b in Button]
            raise ValueError(
                f"Invalid button: {value}. Must be one of: {valid}"
            ) from exc

    @staticmethod
    def to_session_state(value: str) -> SessionState:
        try:
            return SessionState[value.upper()]
        except KeyError as exc:
            valid = [s.name.lower() for s in SessionState]
            raise ValueError(
                f"Invalid session_state: {value}. Must be one of: {valid}"
            ) from exc

    @staticmethod
    def to_timedelta_seconds(value: object, field: str = "interval") -> timedelta:
        if isinstance(value, (int, float)):
            return timedelta(seconds=value)
        raise ValueError(f"Invalid {field}: expected seconds as number")

    @staticmethod
    def to_str(value: object) -> str:
        if value is None:
            raise ValueError("Value is required")
        return str(value)

    @staticmethod
    def to_int(value: object, field: str = "value") -> int:
        if isinstance(value, (int, float)):
            return int(value)
        raise ValueError(f"Invalid {field}: expected number")

    @staticmethod
    def to_float(value: object, field: str = "value") -> float:
        if isinstance(value, (int, float)):
            return float(value)
        raise ValueError(f"Invalid {field}: expected number")

    @staticmethod
    def to_bool(value: object, field: str = "value") -> bool:
        if isinstance(value, bool):
            return value
        raise ValueError(f"Invalid {field}: expected boolean")

    @staticmethod
    def require_str_dict(value: object, field: str = "body") -> dict[str, object]:
        if not isinstance(value, dict):
            raise ValueError(f"Invalid {field}: expected JSON object")
        return value

    @staticmethod
    def enum_name(value: object) -> str:
        if hasattr(value, "name"):
            return value.name
        return str(value)

    @staticmethod
    def timedelta_seconds(value: timedelta) -> float:
        return value.total_seconds()

    @staticmethod
    def uuid_str(value: object) -> str:
        return str(value)
