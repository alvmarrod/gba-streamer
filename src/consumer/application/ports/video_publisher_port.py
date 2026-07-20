from abc import ABC, abstractmethod


class VideoPublisherPort(ABC):
    @abstractmethod
    async def publish(self) -> None: ...
