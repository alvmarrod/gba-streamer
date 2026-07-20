import pytest

from consumer.application.ports.video_publisher_port import VideoPublisherPort


class TestVideoPublisherPort:
    def test_is_abstract(self) -> None:
        with pytest.raises(TypeError):
            VideoPublisherPort()  # type: ignore[abstract]

    def test_concrete_subclass(self) -> None:
        class Stub(VideoPublisherPort):
            async def publish(self) -> None:
                pass

        port = Stub()
        assert port is not None
