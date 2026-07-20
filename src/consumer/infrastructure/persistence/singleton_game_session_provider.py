from __future__ import annotations

from consumer.application.ports.game_session_provider import GameSessionProvider
from consumer.domain.entities.game_session import GameSession


class SingletonGameSessionProvider(GameSessionProvider):
    def __init__(self, session: GameSession) -> None:
        self._session = session

    async def get_session(self) -> GameSession:
        return self._session
