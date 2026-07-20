from __future__ import annotations

import logging

from consumer.infrastructure.monitoring.json_formatter import JsonFormatter


def test_json_formatter_plain(benchmark: object) -> None:
    formatter = JsonFormatter()

    def _run() -> str:
        record = logging.LogRecord(
            name="gba_streamer",
            level=logging.INFO,
            pathname="",
            lineno=0,
            msg="application_started",
            args=(),
            exc_info=None,
        )
        return formatter.format(record)

    benchmark(_run)  # type: ignore[operator]


def test_json_formatter_with_extra(benchmark: object) -> None:
    formatter = JsonFormatter()

    def _run() -> str:
        record = logging.LogRecord(
            name="gba_streamer",
            level=logging.INFO,
            pathname="",
            lineno=0,
            msg="request_completed",
            args=(),
            exc_info=None,
        )
        record.method = "GET"  # type: ignore[attr-defined]
        record.status = 200
        record.duration_ms = 1.5
        return formatter.format(record)

    benchmark(_run)  # type: ignore[operator]


def test_json_formatter_with_exception(benchmark: object) -> None:
    formatter = JsonFormatter()
    exc = ValueError("disk full")

    def _run() -> str:
        record = logging.LogRecord(
            name="gba_streamer",
            level=logging.ERROR,
            pathname="",
            lineno=0,
            msg="save_failed",
            args=(),
            exc_info=(ValueError, exc, None),
        )
        return formatter.format(record)

    benchmark(_run)  # type: ignore[operator]
