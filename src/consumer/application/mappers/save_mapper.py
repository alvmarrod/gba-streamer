from __future__ import annotations

from consumer.domain.value_objects import SaveMetadata

from consumer.application.dto.save import AutosaveResponse, ManualSaveResponse


class SaveMapper:
    @staticmethod
    def to_autosave_response(metadata: SaveMetadata) -> AutosaveResponse:
        return AutosaveResponse(
            last_save_at=metadata.last_save_at,
            save_count=metadata.save_count,
        )

    @staticmethod
    def to_manual_save_response(metadata: SaveMetadata) -> ManualSaveResponse:
        return ManualSaveResponse(
            last_save_at=metadata.last_save_at,
            save_count=metadata.save_count,
        )
