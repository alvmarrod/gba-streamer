from __future__ import annotations

from collections import deque

from consumer.domain.value_objects import GameInput

_MAX_SIZE = 5


class InputHistory:
    def __init__(self) -> None:
        self._history: deque[GameInput] = deque(maxlen=_MAX_SIZE)

    def record(self, game_input: GameInput) -> None:
        self._history.append(game_input)

    @property
    def entries(self) -> list[GameInput]:
        return list(self._history)
