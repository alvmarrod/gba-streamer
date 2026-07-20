from __future__ import annotations


from consumer.application.ports.configuration_provider_port import (
    ConfigurationProviderPort,
)
from consumer.application.ports.emulator_control_port import EmulatorControlPort
from consumer.application.ports.framebuffer_provider_port import (
    FramebufferProviderPort,
)
from consumer.application.ports.game_session_provider import GameSessionProvider
from consumer.application.ports.logger_port import LoggerPort
from consumer.application.ports.metrics_publisher_port import MetricsPublisherPort
from consumer.application.ports.save_repository_port import SaveRepositoryPort
from consumer.application.ports.snapshot_port import SnapshotPort
from consumer.application.ports.video_publisher_port import VideoPublisherPort
from consumer.domain.entities.game_session import GameSession
from consumer.domain.services.metrics_calculator import MetricsSnapshot
from consumer.domain.value_objects import GameInput, SessionConfiguration


class StubSessionProvider(GameSessionProvider):
    def __init__(self, session: GameSession) -> None:
        self._session = session

    async def get_session(self) -> GameSession:
        return self._session


class StubLogger(LoggerPort):
    async def debug(self, message: str, **kwargs: object) -> None: ...
    async def info(self, message: str, **kwargs: object) -> None: ...
    async def warning(self, message: str, **kwargs: object) -> None: ...
    async def error(self, message: str, **kwargs: object) -> None: ...


class StubLoggerRecording(LoggerPort):
    def __init__(self) -> None:
        self.calls: list[tuple[str, dict[str, object]]] = []

    async def debug(self, message: str, **kwargs: object) -> None:
        self.calls.append((message, kwargs))

    async def info(self, message: str, **kwargs: object) -> None:
        self.calls.append((message, kwargs))

    async def warning(self, message: str, **kwargs: object) -> None:
        self.calls.append((message, kwargs))

    async def error(self, message: str, **kwargs: object) -> None:
        self.calls.append((message, kwargs))


class StubSnapshotPort(SnapshotPort):
    def __init__(self, data: bytes = b"snapshot-bytes") -> None:
        self._data = data
        self.restored: bytes | None = None

    async def create_snapshot(self) -> bytes:
        return self._data

    async def restore_snapshot(self, data: bytes) -> None:
        self.restored = data


class StubSaveRepository(SaveRepositoryPort):
    def __init__(self, data: bytes = b"") -> None:
        self._data = data
        self.saved: bytes | None = None

    async def save(self, data: bytes) -> None:
        self.saved = data

    async def load(self) -> bytes:
        return self._data


class StubVideoPublisher(VideoPublisherPort):
    def __init__(self) -> None:
        self.publish_count = 0

    async def publish(self) -> None:
        self.publish_count += 1


class StubFramebufferProvider(FramebufferProviderPort):
    def __init__(self, data: bytes | None = None) -> None:
        self._data = data or b"\x80\x90\xa0\xff" * (160 * 144)

    async def get_framebuffer(self) -> bytes:
        return self._data


class StubEmulatorControl(EmulatorControlPort):
    def __init__(self) -> None:
        self.executed: list[GameInput] = []
        self.tick_count = 0

    async def execute_input(self, game_input: GameInput) -> None:
        self.executed.append(game_input)

    async def tick(self) -> None:
        self.tick_count += 1


class StubMetricsPublisher(MetricsPublisherPort):
    def __init__(self) -> None:
        self.published: MetricsSnapshot | None = None

    async def publish(self, metrics: MetricsSnapshot) -> None:
        self.published = metrics


class StubConfigurationProvider(ConfigurationProviderPort):
    def __init__(self, config: SessionConfiguration) -> None:
        self._config = config

    async def load(self) -> SessionConfiguration:
        return self._config

    async def reload(self) -> SessionConfiguration:
        return self._config
