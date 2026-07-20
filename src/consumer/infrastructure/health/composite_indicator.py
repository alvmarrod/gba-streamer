from __future__ import annotations

import tempfile

from consumer.application.ports.health_indicator_port import HealthIndicatorPort
from consumer.application.scheduler.scheduler import Scheduler
from consumer.infrastructure.emulator.pyboy_adapter import PyBoyAdapter
from consumer.infrastructure.persistence.file_save_repository import FileSaveRepository
from consumer.infrastructure.streaming.aiortc_video_publisher import (
    AiortcVideoPublisher,
)


class CompositeHealthIndicator(HealthIndicatorPort):
    def __init__(
        self,
        scheduler: Scheduler,
        pyboy: PyBoyAdapter,
        save_repository: FileSaveRepository,
        publisher: AiortcVideoPublisher,
    ) -> None:
        self._scheduler = scheduler
        self._pyboy = pyboy
        self._save_repository = save_repository
        self._publisher = publisher

    async def check(self) -> list[dict[str, object]]:
        return [
            self._check_scheduler(),
            self._check_emulator(),
            self._check_persistence(),
            self._check_streaming(),
        ]

    def _check_scheduler(self) -> dict[str, object]:
        return {
            "component": "scheduler",
            "healthy": self._scheduler.task_count > 0,
        }

    def _check_emulator(self) -> dict[str, object]:
        try:
            self._pyboy._executor  # type: ignore[attr-defined]
            return {"component": "emulator", "healthy": True}
        except Exception:
            return {"component": "emulator", "healthy": False}

    def _check_persistence(self) -> dict[str, object]:
        try:
            with tempfile.NamedTemporaryFile(
                dir=self._save_repository._save_dir,  # type: ignore[attr-defined]
                delete=True,
            ):
                pass
            return {"component": "persistence", "healthy": True}
        except Exception:
            return {"component": "persistence", "healthy": False}

    def _check_streaming(self) -> dict[str, object]:
        try:
            self._publisher._source_track  # type: ignore[attr-defined]
            return {"component": "streaming", "healthy": True}
        except Exception:
            return {"component": "streaming", "healthy": False}
