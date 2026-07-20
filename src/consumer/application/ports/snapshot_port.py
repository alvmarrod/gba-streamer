from abc import ABC, abstractmethod


class SnapshotPort(ABC):
    @abstractmethod
    async def create_snapshot(self) -> bytes: ...

    @abstractmethod
    async def restore_snapshot(self, data: bytes) -> None: ...
