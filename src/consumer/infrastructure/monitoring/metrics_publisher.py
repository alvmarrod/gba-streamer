from __future__ import annotations

import json

from consumer.application.ports.logger_port import LoggerPort
from consumer.application.ports.metrics_publisher_port import MetricsPublisherPort
from consumer.domain.services.metrics_calculator import MetricsSnapshot


class MetricsPublisher(MetricsPublisherPort):
    def __init__(self, logger: LoggerPort) -> None:
        self._logger = logger

    async def publish(self, metrics: MetricsSnapshot) -> None:
        payload = {
            "total_commands": metrics.total_commands,
            "connected_players": metrics.connected_players,
            "total_players_seen": metrics.total_players_seen,
            "votes_processed": metrics.votes_processed,
            "frames_executed": metrics.frames_executed,
            "commands_per_minute": round(metrics.commands_per_minute, 2),
            "active_player_ratio": round(metrics.active_player_ratio, 2),
        }
        await self._logger.info(json.dumps(payload))
