from dataclasses import dataclass

from consumer.domain.enums import Button


@dataclass(frozen=True)
class ResolveVoteRequest:
    pass


@dataclass(frozen=True)
class ResolveVoteResponse:
    winning_button: Button | None = None
    vote_count: int = 0
