from __future__ import annotations

import logging
from typing import Any

from consumer.application.ports.logger_port import LoggerPort


class LoggerAdapter(LoggerPort):
    def __init__(self, logger: logging.Logger) -> None:
        self._logger = logger

    async def debug(self, message: str, **kwargs: Any) -> None:
        self._logger.debug(message, **kwargs)

    async def info(self, message: str, **kwargs: Any) -> None:
        self._logger.info(message, **kwargs)

    async def warning(self, message: str, **kwargs: Any) -> None:
        self._logger.warning(message, **kwargs)

    async def error(self, message: str, **kwargs: Any) -> None:
        self._logger.error(message, **kwargs)
