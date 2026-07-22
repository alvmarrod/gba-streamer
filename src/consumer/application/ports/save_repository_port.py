from abc import ABC, abstractmethod
from typing import Any


class SaveRepositoryPort(ABC):
    @abstractmethod
    async def save(self, data: bytes) -> None: ...

    @abstractmethod
    async def load(self) -> bytes: ...

    @abstractmethod
    async def save_metadata(self, metadata: dict[str, Any]) -> None: ...

    @abstractmethod
    async def load_metadata(self) -> dict[str, Any]: ...
