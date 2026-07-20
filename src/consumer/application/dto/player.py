from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True)
class ConnectPlayerRequest:
    player_id: UUID
    display_name: str


@dataclass(frozen=True)
class ConnectPlayerResponse:
    player_id: UUID
    display_name: str


@dataclass(frozen=True)
class DisconnectPlayerRequest:
    player_id: UUID


@dataclass(frozen=True)
class DisconnectPlayerResponse:
    pass
