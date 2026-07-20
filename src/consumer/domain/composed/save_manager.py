from __future__ import annotations

from datetime import datetime

from consumer.domain.value_objects import SaveMetadata


class SaveManager:
    def __init__(self) -> None:
        self._metadata: SaveMetadata | None = None
        self._has_pending_snapshot: bool = False

    @property
    def metadata(self) -> SaveMetadata | None:
        return self._metadata

    @property
    def has_pending_snapshot(self) -> bool:
        return self._has_pending_snapshot

    def create_snapshot(self) -> None:
        self._has_pending_snapshot = True

    def restore_snapshot(self) -> None:
        self._has_pending_snapshot = False

    def update_metadata(self, timestamp: datetime) -> None:
        save_count = (self._metadata.save_count + 1) if self._metadata else 1
        self._metadata = SaveMetadata(last_save_at=timestamp, save_count=save_count)
