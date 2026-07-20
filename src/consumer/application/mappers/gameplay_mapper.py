from __future__ import annotations

from datetime import datetime, timezone

from consumer.domain.value_objects import GameInput, PlayerId

from consumer.application.dto.gameplay import SubmitInputRequest


class GameplayMapper:
    @staticmethod
    def to_game_input(request: SubmitInputRequest) -> GameInput:
        return GameInput(
            button=request.button,
            timestamp=datetime.now(tz=timezone.utc),
            player_id=PlayerId(value=request.player_id),
        )
