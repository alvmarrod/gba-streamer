import pytest

from consumer.application.ports.framebuffer_provider_port import (
    FramebufferProviderPort,
)


class TestFramebufferProviderPort:
    def test_is_abstract(self) -> None:
        with pytest.raises(TypeError):
            FramebufferProviderPort()  # type: ignore[abstract]

    def test_concrete_subclass(self) -> None:
        class Stub(FramebufferProviderPort):
            async def get_framebuffer(self) -> bytes:
                return b""

        port = Stub()
        assert port is not None
