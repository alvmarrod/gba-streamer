from datetime import datetime, timezone

import pytest

from consumer.application.dto.save import (
    AutosaveRequest,
    AutosaveResponse,
    ManualSaveRequest,
    ManualSaveResponse,
)


class TestAutosaveDTOs:
    def test_request_construction(self) -> None:
        req = AutosaveRequest()
        assert req is not None

    def test_response_construction(self) -> None:
        now = datetime.now(tz=timezone.utc)
        resp = AutosaveResponse(last_save_at=now, save_count=3)
        assert resp.last_save_at == now
        assert resp.save_count == 3

    def test_response_immutability(self) -> None:
        resp = AutosaveResponse(
            last_save_at=datetime.now(tz=timezone.utc), save_count=1
        )
        with pytest.raises(AttributeError):
            resp.save_count = 5  # type: ignore[misc]


class TestManualSaveDTOs:
    def test_request_construction(self) -> None:
        req = ManualSaveRequest()
        assert req is not None

    def test_response_construction(self) -> None:
        now = datetime.now(tz=timezone.utc)
        resp = ManualSaveResponse(last_save_at=now, save_count=1)
        assert resp.last_save_at == now
        assert resp.save_count == 1

    def test_response_immutability(self) -> None:
        resp = ManualSaveResponse(
            last_save_at=datetime.now(tz=timezone.utc), save_count=1
        )
        with pytest.raises(AttributeError):
            resp.last_save_at = datetime.now(tz=timezone.utc)  # type: ignore[misc]
