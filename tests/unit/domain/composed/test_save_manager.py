from datetime import datetime

from consumer.domain.composed.save_manager import SaveManager


class TestSaveManager:
    def test_initial_state(self) -> None:
        sm = SaveManager()
        assert sm.metadata is None
        assert sm.has_pending_snapshot is False

    def test_create_snapshot(self) -> None:
        sm = SaveManager()
        sm.create_snapshot()
        assert sm.has_pending_snapshot is True

    def test_restore_snapshot_clears_flag(self) -> None:
        sm = SaveManager()
        sm.create_snapshot()
        sm.restore_snapshot()
        assert sm.has_pending_snapshot is False

    def test_update_metadata_first_time(self) -> None:
        sm = SaveManager()
        ts = datetime(2026, 1, 1, 12, 0, 0)
        sm.update_metadata(ts)
        assert sm.metadata is not None
        assert sm.metadata.last_save_at == ts
        assert sm.metadata.save_count == 1

    def test_update_metadata_increments_count(self) -> None:
        sm = SaveManager()
        ts1 = datetime(2026, 1, 1, 12, 0, 0)
        ts2 = datetime(2026, 1, 1, 12, 0, 15)
        sm.update_metadata(ts1)
        sm.update_metadata(ts2)
        assert sm.metadata is not None
        assert sm.metadata.last_save_at == ts2
        assert sm.metadata.save_count == 2
