from datetime import datetime, timezone

from consumer.application.mappers.save_mapper import SaveMapper
from consumer.domain.value_objects import SaveMetadata


class TestSaveMapper:
    def test_to_autosave_response(self) -> None:
        now = datetime.now(tz=timezone.utc)
        metadata = SaveMetadata(last_save_at=now, save_count=3)
        resp = SaveMapper.to_autosave_response(metadata)

        assert resp.last_save_at == now
        assert resp.save_count == 3

    def test_to_manual_save_response(self) -> None:
        now = datetime.now(tz=timezone.utc)
        metadata = SaveMetadata(last_save_at=now, save_count=1)
        resp = SaveMapper.to_manual_save_response(metadata)

        assert resp.last_save_at == now
        assert resp.save_count == 1
