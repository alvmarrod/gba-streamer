from abc import ABC, abstractmethod

from consumer.domain.services.metrics_calculator import MetricsSnapshot


class MetricsPublisherPort(ABC):
    @abstractmethod
    async def publish(self, metrics: MetricsSnapshot) -> None: ...
