from __future__ import annotations

from collections import defaultdict

from consumer.domain.composed.vote_round import VoteRound
from consumer.domain.enums import Button
from consumer.domain.value_objects import GameInput, VoteResult


class VoteResolver:
    @staticmethod
    def resolve(vote_round: VoteRound) -> VoteResult:
        votes = vote_round.votes
        tally: dict[Button, int] = defaultdict(int)
        first_by_button: dict[Button, GameInput] = {}

        for game_input in votes.values():
            tally[game_input.button] += 1
            if game_input.button not in first_by_button:
                first_by_button[game_input.button] = game_input

        max_count = max(tally.values())
        winners = [b for b, c in tally.items() if c == max_count]

        winning_button = winners[0]
        return VoteResult(
            winning_input=first_by_button[winning_button],
            vote_count=max_count,
        )
