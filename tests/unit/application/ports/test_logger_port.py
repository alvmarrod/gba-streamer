import pytest

from consumer.application.ports.logger_port import LoggerPort


class TestLoggerPort:
    def test_is_abstract(self) -> None:
        with pytest.raises(TypeError):
            LoggerPort()  # type: ignore[abstract]

    def test_concrete_subclass(self) -> None:
        class Stub(LoggerPort):
            async def debug(self, message: str) -> None:
                pass

            async def info(self, message: str) -> None:
                pass

            async def warning(self, message: str) -> None:
                pass

            async def error(self, message: str) -> None:
                pass

        port = Stub()
        assert port is not None
