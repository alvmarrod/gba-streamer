from __future__ import annotations

import logging
from unittest.mock import MagicMock

import pytest

from consumer.infrastructure.monitoring.logger_adapter import LoggerAdapter


@pytest.fixture
def stdlib_logger() -> MagicMock:
    return MagicMock(spec=logging.Logger)


@pytest.fixture
def adapter(stdlib_logger: MagicMock) -> LoggerAdapter:
    return LoggerAdapter(stdlib_logger)


class TestLoggerAdapter:
    async def test_debug(
        self, adapter: LoggerAdapter, stdlib_logger: MagicMock
    ) -> None:
        await adapter.debug("debug msg")
        stdlib_logger.debug.assert_called_once_with("debug msg", extra={})

    async def test_info(self, adapter: LoggerAdapter, stdlib_logger: MagicMock) -> None:
        await adapter.info("info msg")
        stdlib_logger.info.assert_called_once_with("info msg", extra={})

    async def test_warning(
        self, adapter: LoggerAdapter, stdlib_logger: MagicMock
    ) -> None:
        await adapter.warning("warn msg")
        stdlib_logger.warning.assert_called_once_with("warn msg", extra={})

    async def test_error(
        self, adapter: LoggerAdapter, stdlib_logger: MagicMock
    ) -> None:
        await adapter.error("error msg")
        stdlib_logger.error.assert_called_once_with(
            "error msg", extra={}, exc_info=None
        )

    async def test_error_with_exc_info(
        self, adapter: LoggerAdapter, stdlib_logger: MagicMock
    ) -> None:
        await adapter.error("failed", exc_info=True)
        stdlib_logger.error.assert_called_once_with("failed", extra={}, exc_info=True)

    async def test_info_with_semantic_kwargs(
        self, adapter: LoggerAdapter, stdlib_logger: MagicMock
    ) -> None:
        await adapter.info("player connected", player_id="123")
        stdlib_logger.info.assert_called_once_with(
            "player connected", extra={"player_id": "123"}
        )
