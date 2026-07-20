from abc import ABC, abstractmethod

from consumer.domain.entities.game_session import GameSession


class GameSessionProvider(ABC):
    @abstractmethod
    async def get_session(self) -> GameSession: ...
