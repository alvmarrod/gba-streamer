from __future__ import annotations

from typing import Protocol


class HealthCheckable(Protocol):
    async def health_check(self) -> dict[str, object]: ...
