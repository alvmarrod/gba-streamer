from abc import ABC, abstractmethod


class SaveRepositoryPort(ABC):
    @abstractmethod
    async def save(self, data: bytes) -> None: ...

    @abstractmethod
    async def load(self) -> bytes: ...
