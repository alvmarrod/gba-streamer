from __future__ import annotations

import logging
from typing import Any

from consumer.application.ports.logger_port import LoggerPort


class LoggerAdapter(LoggerPort):
    def __init__(self, logger: logging.Logger) -> None:
        self._logger = logger

    async def debug(self, message: str, **kwargs: Any) -> None:
        self._logger.debug(message, extra=self._extra(kwargs))

    async def info(self, message: str, **kwargs: Any) -> None:
        self._logger.info(message, extra=self._extra(kwargs))

    async def warning(self, message: str, **kwargs: Any) -> None:
        self._logger.warning(message, extra=self._extra(kwargs))

    async def error(self, message: str, **kwargs: Any) -> None:
        exc_info = kwargs.pop("exc_info", None)
        self._logger.error(message, extra=self._extra(kwargs), exc_info=exc_info)

    @staticmethod
    def _extra(kwargs: dict[str, Any]) -> dict[str, Any]:
        return {k: v for k, v in kwargs.items() if k != "exc_info"}
