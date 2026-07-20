from __future__ import annotations

from typing import TYPE_CHECKING

from consumer.domain.enums import ControlMode

if TYPE_CHECKING:
    from consumer.domain.entities.game_session import GameSession


class SessionValidator:
    @staticmethod
    def validate(session: GameSession) -> None:
        if session.players.count != session.metrics.connected_players:
            raise ValueError(
                f"Player count mismatch: PlayerManager has {session.players.count} "
                f"but Metrics reports {session.metrics.connected_players} connected"
            )

        if session.metrics.total_players_seen < session.metrics.connected_players:
            raise ValueError(
                f"total_players_seen ({session.metrics.total_players_seen}) "
                f"is less than connected_players ({session.metrics.connected_players})"
            )

        if (
            session.configuration.control_mode == ControlMode.FIFO
            and session.current_vote is not None
        ):
            raise ValueError("FIFO mode active but a VoteRound exists")
