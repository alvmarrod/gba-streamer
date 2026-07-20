import pytest

from consumer.application.ports.emulator_control_port import EmulatorControlPort


class TestEmulatorControlPort:
    def test_is_abstract(self) -> None:
        with pytest.raises(TypeError):
            EmulatorControlPort()  # type: ignore[abstract]

    def test_concrete_subclass(self) -> None:
        class Stub(EmulatorControlPort):
            async def execute_input(self, game_input: object) -> None:
                pass

            async def tick(self) -> None:
                pass

        port = Stub()
        assert port is not None
