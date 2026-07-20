import pytest

from consumer.application.ports.game_session_provider import GameSessionProvider


class TestGameSessionProvider:
    def test_is_abstract(self) -> None:
        with pytest.raises(TypeError):
            GameSessionProvider()  # type: ignore[abstract]

    def test_concrete_subclass(self) -> None:
        class Stub(GameSessionProvider):
            async def get_session(self) -> None:  # type: ignore[override]
                return None

        provider = Stub()
        assert provider is not None
