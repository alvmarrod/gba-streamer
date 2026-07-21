from __future__ import annotations

from consumer.domain.composed.input_queue import InputQueue
from consumer.domain.value_objects import GameInput


class FIFOResolver:
    @staticmethod
    def resolve(input_queue: InputQueue) -> GameInput | None:
        try:
            return input_queue.dequeue()
        except IndexError:
            return None
