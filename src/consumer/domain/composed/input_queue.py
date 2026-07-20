from __future__ import annotations

from collections import deque

from consumer.domain.value_objects import GameInput


class InputQueue:
    def __init__(self) -> None:
        self._queue: deque[GameInput] = deque()

    def enqueue(self, item: GameInput) -> None:
        self._queue.append(item)

    def dequeue(self) -> GameInput:
        if not self._queue:
            raise IndexError("dequeue from empty queue")
        return self._queue.popleft()

    def peek(self) -> GameInput:
        if not self._queue:
            raise IndexError("peek from empty queue")
        return self._queue[0]

    def clear(self) -> None:
        self._queue.clear()

    @property
    def size(self) -> int:
        return len(self._queue)
