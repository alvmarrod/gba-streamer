from __future__ import annotations

from aiohttp import web  # type: ignore[import-untyped]
from aiohttp.test_utils import TestClient, TestServer  # type: ignore[import-untyped]

from consumer.application.ports.logger_port import LoggerPort
from consumer.presentation.middleware.request_logger import request_logger_middleware


class StubLogger(LoggerPort):
    def __init__(self) -> None:
        self.calls: list[tuple[str, dict[str, object]]] = []

    async def debug(self, message: str, **kwargs: object) -> None:
        self.calls.append((message, kwargs))

    async def info(self, message: str, **kwargs: object) -> None:
        self.calls.append((message, kwargs))

    async def warning(self, message: str, **kwargs: object) -> None:
        self.calls.append((message, kwargs))

    async def error(self, message: str, **kwargs: object) -> None:
        self.calls.append((message, kwargs))


def _make_app(logger: LoggerPort) -> web.Application:
    app = web.Application()
    app.middlewares.append(request_logger_middleware(logger))  # type: ignore[arg-type]

    async def _ok(request: web.Request) -> web.Response:
        return web.json_response({"ok": True})

    async def _fail(request: web.Request) -> web.Response:
        raise ValueError("test error")

    app.router.add_get("/ok", _ok)
    app.router.add_get("/fail", _fail)
    return app


class TestRequestLoggerSuccess:
    async def test_logs_completed_request(self) -> None:
        logger = StubLogger()
        async with TestClient(TestServer(_make_app(logger))) as client:
            resp = await client.get("/ok")
            assert resp.status == 200

        info_calls = [c for c in logger.calls if c[0] == "request_completed"]
        assert len(info_calls) == 1
        _, kwargs = info_calls[0]
        assert kwargs["method"] == "GET"
        assert kwargs["path"] == "/ok"
        assert kwargs["status"] == 200
        assert "duration_ms" in kwargs

    async def test_duration_is_positive(self) -> None:
        logger = StubLogger()
        async with TestClient(TestServer(_make_app(logger))) as client:
            await client.get("/ok")

        info_calls = [c for c in logger.calls if c[0] == "request_completed"]
        _, kwargs = info_calls[0]
        duration: float = kwargs["duration_ms"]  # type: ignore[assignment]
        assert duration >= 0


class TestRequestLoggerFailure:
    async def test_logs_failed_request(self) -> None:
        logger = StubLogger()
        async with TestClient(TestServer(_make_app(logger))) as client:
            try:
                await client.get("/fail")
            except ValueError:
                pass

        error_calls = [c for c in logger.calls if c[0] == "request_failed"]
        assert len(error_calls) == 1
        _, kwargs = error_calls[0]
        assert kwargs["method"] == "GET"
        assert kwargs["path"] == "/fail"
        assert "duration_ms" in kwargs

    async def test_does_not_log_completed_on_failure(self) -> None:
        logger = StubLogger()
        async with TestClient(TestServer(_make_app(logger))) as client:
            try:
                await client.get("/fail")
            except ValueError:
                pass

        info_calls = [c for c in logger.calls if c[0] == "request_completed"]
        assert len(info_calls) == 0
