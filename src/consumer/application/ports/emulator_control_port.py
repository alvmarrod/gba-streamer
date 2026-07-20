from abc import ABC, abstractmethod

from consumer.domain.value_objects import GameInput


class EmulatorControlPort(ABC):
    @abstractmethod
    async def execute_input(self, game_input: GameInput) -> None: ...

    @abstractmethod
    async def tick(self) -> None: ...
