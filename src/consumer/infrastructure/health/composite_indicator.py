from __future__ import annotations

from consumer.application.ports.health_checkable import HealthCheckable
from consumer.application.ports.health_indicator_port import HealthIndicatorPort


class CompositeHealthIndicator(HealthIndicatorPort):
    def __init__(self, components: list[HealthCheckable]) -> None:
        self._components = components

    async def check(self) -> list[dict[str, object]]:
        results: list[dict[str, object]] = []
        for component in self._components:
            try:
                result = await component.health_check()
            except Exception:
                result = {"component": "unknown", "healthy": False}
            results.append(result)
        return results
