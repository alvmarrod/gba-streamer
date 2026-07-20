from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class LoggerPort(ABC):
    @abstractmethod
    async def debug(self, message: str, **kwargs: Any) -> None: ...

    @abstractmethod
    async def info(self, message: str, **kwargs: Any) -> None: ...

    @abstractmethod
    async def warning(self, message: str, **kwargs: Any) -> None: ...

    @abstractmethod
    async def error(self, message: str, **kwargs: Any) -> None: ...
