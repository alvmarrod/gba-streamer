import pytest

from consumer.application.ports.snapshot_port import SnapshotPort


class TestSnapshotPort:
    def test_is_abstract(self) -> None:
        with pytest.raises(TypeError):
            SnapshotPort()  # type: ignore[abstract]

    def test_concrete_subclass(self) -> None:
        class Stub(SnapshotPort):
            async def create_snapshot(self) -> bytes:
                return b""

            async def restore_snapshot(self, data: bytes) -> None:
                pass

        port = Stub()
        assert port is not None
