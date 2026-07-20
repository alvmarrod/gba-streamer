from dataclasses import dataclass
from uuid import UUID

from consumer.domain.enums import Button


@dataclass(frozen=True)
class SubmitInputRequest:
    player_id: UUID
    button: Button


@dataclass(frozen=True)
class SubmitInputResponse:
    pass


@dataclass(frozen=True)
class ResolveInputRequest:
    pass


@dataclass(frozen=True)
class ResolveInputResponse:
    pass


@dataclass(frozen=True)
class TickEmulatorRequest:
    pass


@dataclass(frozen=True)
class TickEmulatorResponse:
    pass
