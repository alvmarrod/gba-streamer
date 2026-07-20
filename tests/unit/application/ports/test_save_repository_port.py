import pytest

from consumer.application.ports.save_repository_port import SaveRepositoryPort


class TestSaveRepositoryPort:
    def test_is_abstract(self) -> None:
        with pytest.raises(TypeError):
            SaveRepositoryPort()  # type: ignore[abstract]

    def test_concrete_subclass(self) -> None:
        class Stub(SaveRepositoryPort):
            async def save(self, data: bytes) -> None:
                pass

            async def load(self) -> bytes:
                return b""

        port = Stub()
        assert port is not None
