from uuid import uuid4

from consumer.application.dto.gameplay import SubmitInputRequest
from consumer.application.mappers.gameplay_mapper import GameplayMapper
from consumer.domain.enums import Button
from consumer.domain.value_objects import PlayerId


class TestGameplayMapper:
    def test_to_game_input(self) -> None:
        pid = uuid4()
        req = SubmitInputRequest(player_id=pid, button=Button.UP)
        game_input = GameplayMapper.to_game_input(req)

        assert game_input.button == Button.UP
        assert game_input.player_id == PlayerId(value=pid)
        assert game_input.timestamp is not None
        assert game_input.timestamp.tzinfo is not None

    def test_to_game_input_preserves_button(self) -> None:
        pid = uuid4()
        req = SubmitInputRequest(player_id=pid, button=Button.SELECT)
        game_input = GameplayMapper.to_game_input(req)

        assert game_input.button == Button.SELECT
