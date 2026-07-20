from __future__ import annotations

from unittest.mock import AsyncMock


from consumer.application.ports.video_publisher_port import VideoPublisherPort


class StubVideoPublisher(VideoPublisherPort):
    def __init__(self) -> None:
        self.publish_count = 0

    async def publish(self) -> None:
        self.publish_count += 1


class TestStubVideoPublisher:
    async def test_implements_port(self) -> None:
        publisher = StubVideoPublisher()
        assert isinstance(publisher, VideoPublisherPort)

    async def test_publish_increments_count(self) -> None:
        publisher = StubVideoPublisher()
        await publisher.publish()
        await publisher.publish()
        assert publisher.publish_count == 2

    async def test_mock_based_stub(self) -> None:
        mock = AsyncMock(spec=VideoPublisherPort)
        await mock.publish()
        mock.publish.assert_called_once()
