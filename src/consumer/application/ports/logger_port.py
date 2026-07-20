from abc import ABC, abstractmethod


class LoggerPort(ABC):
    @abstractmethod
    async def debug(self, message: str) -> None: ...

    @abstractmethod
    async def info(self, message: str) -> None: ...

    @abstractmethod
    async def warning(self, message: str) -> None: ...

    @abstractmethod
    async def error(self, message: str) -> None: ...
