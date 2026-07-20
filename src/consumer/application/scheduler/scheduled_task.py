from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import timedelta


class ScheduledTask(ABC):
    @property
    @abstractmethod
    def name(self) -> str: ...

    @property
    @abstractmethod
    def interval(self) -> timedelta: ...

    @abstractmethod
    async def execute(self) -> None: ...
