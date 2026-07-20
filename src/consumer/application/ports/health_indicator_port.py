from __future__ import annotations

from abc import ABC, abstractmethod


class HealthIndicatorPort(ABC):
    @abstractmethod
    async def check(self) -> list[dict[str, object]]: ...
