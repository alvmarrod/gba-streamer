from __future__ import annotations

from datetime import datetime, timedelta
from uuid import uuid4

from consumer.domain.entities.game_session import GameSession
from consumer.domain.enums import Button, ControlMode
from consumer.domain.value_objects import (
    GameInput,
    PlayerId,
    SessionConfiguration,
    SessionId,
)


def make_session(
    control_mode: ControlMode = ControlMode.FIFO,
) -> GameSession:
    config = SessionConfiguration(
        control_mode=control_mode,
        voting_interval=timedelta(seconds=1),
        autosave_interval=timedelta(seconds=15),
    )
    return GameSession(
        session_id=SessionId(value=uuid4()),
        configuration=config,
    )


def make_player_id() -> PlayerId:
    return PlayerId(value=uuid4())


def make_game_input(
    button: Button = Button.A,
    player_id: PlayerId | None = None,
) -> GameInput:
    return GameInput(
        button=button,
        timestamp=datetime(2026, 1, 1, 12, 0, 0),
        player_id=player_id or make_player_id(),
    )
