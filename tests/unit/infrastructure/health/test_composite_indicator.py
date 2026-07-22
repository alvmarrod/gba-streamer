from __future__ import annotations

import tempfile
from datetime import timedelta
from pathlib import Path


from consumer.application.ports.health_checkable import HealthCheckable
from consumer.application.scheduler.scheduled_task import ScheduledTask
from consumer.application.scheduler.scheduler import Scheduler
from consumer.infrastructure.health.composite_indicator import (
    CompositeHealthIndicator,
)
from consumer.infrastructure.persistence.file_save_repository import (
    FileSaveRepository,
)
from consumer.infrastructure.telegram.rabbitmq_adapter import (
    RabbitMQTelegramAdapter,
)

from tests.helpers.stub_providers import StubLogger


class _StubTask(ScheduledTask):
    def __init__(self, task_name: str = "stub", interval_ms: int = 1000) -> None:
        self._name = task_name
        self._interval = timedelta(milliseconds=interval_ms)

    @property
    def name(self) -> str:
        return self._name

    @property
    def interval(self) -> timedelta:
        return self._interval

    async def execute(self) -> None:
        pass


class TestCompositeHealthIndicator:
    async def test_aggregates_all_components(self) -> None:
        class Healthy(HealthCheckable):
            async def health_check(self) -> dict[str, object]:
                return {"component": "test", "healthy": True}

        class Unhealthy(HealthCheckable):
            async def health_check(self) -> dict[str, object]:
                return {"component": "test2", "healthy": False}

        indicator = CompositeHealthIndicator([Healthy(), Unhealthy()])
        results = await indicator.check()

        assert len(results) == 2
        assert results[0]["healthy"] is True
        assert results[1]["healthy"] is False

    async def test_component_exception_reported_as_unhealthy(self) -> None:
        class Failing(HealthCheckable):
            async def health_check(self) -> dict[str, object]:
                raise RuntimeError("boom")

        indicator = CompositeHealthIndicator([Failing()])
        results = await indicator.check()

        assert len(results) == 1
        assert results[0]["healthy"] is False

    async def test_empty_components_returns_empty_list(self) -> None:
        indicator = CompositeHealthIndicator([])
        results = await indicator.check()
        assert results == []


class TestSchedulerHealthCheck:
    async def test_healthy_when_running_with_tasks(self) -> None:
        logger = StubLogger()
        scheduler = Scheduler(logger)
        task = _StubTask(task_name="test_task")
        scheduler.register(task)
        scheduler.start()

        result = await scheduler.health_check()
        assert result["component"] == "scheduler"
        assert result["healthy"] is True
        assert result["running"] is True
        assert result["task_count"] == 1
        assert result["tasks"] == ["test_task"]

        await scheduler.stop()

    async def test_unhealthy_when_not_running(self) -> None:
        logger = StubLogger()
        scheduler = Scheduler(logger)
        task = _StubTask(task_name="test_task")
        scheduler.register(task)

        result = await scheduler.health_check()
        assert result["healthy"] is False
        assert result["running"] is False

    async def test_unhealthy_when_no_tasks_registered(self) -> None:
        logger = StubLogger()
        scheduler = Scheduler(logger)

        result = await scheduler.health_check()
        assert result["healthy"] is False
        assert result["task_count"] == 0

    async def test_running_property_exposed(self) -> None:
        logger = StubLogger()
        scheduler = Scheduler(logger)

        assert scheduler.running is False
        scheduler.start()
        assert scheduler.running is True
        await scheduler.stop()
        assert scheduler.running is False


class TestFileSaveRepositoryHealthCheck:
    async def test_writes_reads_and_verifies(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            repo = FileSaveRepository(Path(tmpdir))
            result = await repo.health_check()

            assert result["component"] == "persistence"
            assert result["healthy"] is True

    async def test_unhealthy_on_readonly_dir(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir)
            path.chmod(0o500)
            repo = FileSaveRepository(path)
            try:
                result = await repo.health_check()
                assert result["healthy"] is False
            finally:
                path.chmod(0o700)

    async def test_cleans_up_temp_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir)
            repo = FileSaveRepository(path)
            await repo.health_check()

            temp_files = list(path.glob(".health_check_tmp"))
            assert len(temp_files) == 0


class TestRabbitMQHealthCheck:
    async def test_healthy_when_connected(self) -> None:
        adapter = RabbitMQTelegramAdapter()
        adapter._connection = _FakeOpenConnection()  # type: ignore[assignment,attr-defined]
        adapter._channel = _FakeOpenChannel()  # type: ignore[assignment,attr-defined]

        result = await adapter.health_check()
        assert result["component"] == "rabbitmq"
        assert result["healthy"] is True
        assert result["connection_open"] is True
        assert result["channel_open"] is True

    async def test_unhealthy_when_not_connected(self) -> None:
        adapter = RabbitMQTelegramAdapter()

        result = await adapter.health_check()
        assert result["healthy"] is False

    async def test_unhealthy_when_channel_closed(self) -> None:
        adapter = RabbitMQTelegramAdapter()
        adapter._connection = _FakeOpenConnection()  # type: ignore[assignment,attr-defined]
        adapter._channel = _FakeClosedChannel()  # type: ignore[assignment,attr-defined]

        result = await adapter.health_check()
        assert result["healthy"] is False
        assert result["channel_open"] is False


class _FakeOpenConnection:
    is_closed = False


class _FakeOpenChannel:
    is_closed = False


class _FakeClosedChannel:
    is_closed = True
