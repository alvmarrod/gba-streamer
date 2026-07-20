from __future__ import annotations

import json
import logging

from consumer.infrastructure.monitoring.json_formatter import JsonFormatter


class TestJsonFormatter:
    def test_plain_message(self) -> None:
        formatter = JsonFormatter()
        record = logging.LogRecord(
            name="gba_streamer",
            level=logging.INFO,
            pathname="",
            lineno=0,
            msg="application_started",
            args=(),
            exc_info=None,
        )
        result = formatter.format(record)
        parsed = json.loads(result)
        assert parsed["event"] == "application_started"
        assert parsed["level"] == "INFO"
        assert parsed["logger"] == "gba_streamer"
        assert "timestamp" in parsed

    def test_message_with_format_args(self) -> None:
        formatter = JsonFormatter()
        record = logging.LogRecord(
            name="gba_streamer",
            level=logging.INFO,
            pathname="",
            lineno=0,
            msg="player %s connected",
            args=("Alice",),
            exc_info=None,
        )
        result = formatter.format(record)
        parsed = json.loads(result)
        assert parsed["event"] == "player Alice connected"

    def test_message_with_extra_fields(self) -> None:
        formatter = JsonFormatter()
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

        result = formatter.format(record)
        parsed = json.loads(result)
        assert parsed["method"] == "GET"
        assert parsed["status"] == 200
        assert parsed["duration_ms"] == 1.5

    def test_error_with_exception(self) -> None:
        formatter = JsonFormatter()
        exc_value = ValueError("disk full")
        record = logging.LogRecord(
            name="gba_streamer",
            level=logging.ERROR,
            pathname="",
            lineno=0,
            msg="save_failed",
            args=(),
            exc_info=(ValueError, exc_value, None),
        )
        result = formatter.format(record)
        parsed = json.loads(result)
        assert parsed["event"] == "save_failed"
        assert parsed["level"] == "ERROR"
        assert parsed["exception"] == "disk full"

    def test_skips_standard_attrs(self) -> None:
        formatter = JsonFormatter()
        record = logging.LogRecord(
            name="gba_streamer",
            level=logging.INFO,
            pathname="/app/main.py",
            lineno=42,
            msg="test",
            args=(),
            exc_info=None,
        )
        result = formatter.format(record)
        parsed = json.loads(result)
        assert "pathname" not in parsed
        assert "lineno" not in parsed
        assert "name" not in parsed
        assert "msg" not in parsed
        assert "filename" not in parsed
