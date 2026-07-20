from dataclasses import dataclass
from datetime import datetime, timedelta
from uuid import UUID

from consumer.domain.enums import Button, ControlMode


@dataclass(frozen=True)
class SessionId:
    value: UUID


@dataclass(frozen=True)
class PlayerId:
    value: UUID


@dataclass(frozen=True)
class GameInput:
    button: Button
    timestamp: datetime
    player_id: PlayerId


@dataclass(frozen=True)
class SessionConfiguration:
    control_mode: ControlMode
    voting_interval: timedelta
    autosave_interval: timedelta


@dataclass(frozen=True)
class SaveMetadata:
    last_save_at: datetime
    save_count: int


@dataclass(frozen=True)
class PlayerStatistics:
    submitted_commands: int
    winning_votes: int
    connected_duration: timedelta


@dataclass(frozen=True)
class VoteResult:
    winning_input: GameInput
    vote_count: int
