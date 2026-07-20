from __future__ import annotations

from aiohttp import web  # type: ignore[import-untyped]

from consumer.application.ports.logger_port import LoggerPort
from consumer.presentation.middleware.cors import cors_middleware
from consumer.presentation.middleware.error_handler import error_handler_middleware
from consumer.presentation.middleware.request_logger import request_logger_middleware


def setup_middleware(app: web.Application, logger: LoggerPort) -> None:
    app.middlewares.append(cors_middleware)  # type: ignore[arg-type]
    app.middlewares.append(error_handler_middleware)  # type: ignore[arg-type]
    app.middlewares.append(request_logger_middleware(logger))  # type: ignore[arg-type]
