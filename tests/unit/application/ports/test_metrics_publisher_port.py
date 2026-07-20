import pytest

from consumer.application.ports.metrics_publisher_port import MetricsPublisherPort


class TestMetricsPublisherPort:
    def test_is_abstract(self) -> None:
        with pytest.raises(TypeError):
            MetricsPublisherPort()  # type: ignore[abstract]

    def test_concrete_subclass(self) -> None:
        from consumer.domain.services.metrics_calculator import MetricsSnapshot

        class Stub(MetricsPublisherPort):
            async def publish(self, metrics: MetricsSnapshot) -> None:
                pass

        port = Stub()
        assert port is not None
