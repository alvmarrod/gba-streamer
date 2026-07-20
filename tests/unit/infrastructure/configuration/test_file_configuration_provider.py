from __future__ import annotations

from pathlib import Path
from textwrap import dedent

import pytest

from consumer.domain.enums import ControlMode
from consumer.infrastructure.configuration.file_configuration_provider import (
    FileConfigurationProvider,
)


@pytest.fixture
def config_dir(tmp_path: Path) -> Path:
    return tmp_path / "config"


class TestFileConfigurationProviderLoad:
    async def test_valid_yaml_full(self, config_dir: Path) -> None:
        config_dir.mkdir(parents=True)
        config_file = config_dir / "config.yaml"
        config_file.write_text(
            dedent("""\
                control_mode: VOTING
                voting_interval: 60
                autosave_interval: 30
            """)
        )
        provider = FileConfigurationProvider(config_file)
        result = await provider.load()

        assert result.control_mode == ControlMode.VOTING
        assert result.voting_interval.total_seconds() == 60
        assert result.autosave_interval.total_seconds() == 30

    async def test_valid_yaml_defaults(self, config_dir: Path) -> None:
        config_dir.mkdir(parents=True)
        config_file = config_dir / "config.yaml"
        config_file.write_text("control_mode: FIFO\n")
        provider = FileConfigurationProvider(config_file)
        result = await provider.load()

        assert result.control_mode == ControlMode.FIFO
        assert result.voting_interval.total_seconds() == 30
        assert result.autosave_interval.total_seconds() == 15

    async def test_empty_yaml_uses_defaults(self, config_dir: Path) -> None:
        config_dir.mkdir(parents=True)
        config_file = config_dir / "config.yaml"
        config_file.write_text("")
        provider = FileConfigurationProvider(config_file)
        result = await provider.load()

        assert result.control_mode == ControlMode.FIFO
        assert result.voting_interval.total_seconds() == 30
        assert result.autosave_interval.total_seconds() == 15

    async def test_none_yaml_uses_defaults(self, config_dir: Path) -> None:
        config_dir.mkdir(parents=True)
        config_file = config_dir / "config.yaml"
        config_file.write_text("---\n")
        provider = FileConfigurationProvider(config_file)
        result = await provider.load()

        assert result.control_mode == ControlMode.FIFO

    async def test_missing_file_raises(self, config_dir: Path) -> None:
        config_file = config_dir / "missing.yaml"
        provider = FileConfigurationProvider(config_file)

        with pytest.raises(FileNotFoundError):
            await provider.load()

    async def test_invalid_yaml_value_raises(self, config_dir: Path) -> None:
        config_dir.mkdir(parents=True)
        config_file = config_dir / "config.yaml"
        config_file.write_text("control_mode: INVALID\n")
        provider = FileConfigurationProvider(config_file)

        with pytest.raises(ValueError, match="Invalid control_mode"):
            await provider.load()

    async def test_non_dict_yaml_raises(self, config_dir: Path) -> None:
        config_dir.mkdir(parents=True)
        config_file = config_dir / "config.yaml"
        config_file.write_text("- item1\n- item2\n")
        provider = FileConfigurationProvider(config_file)

        with pytest.raises(ValueError, match="Expected YAML mapping"):
            await provider.load()


class TestFileConfigurationProviderReload:
    async def test_reload_reads_new_content(self, config_dir: Path) -> None:
        config_dir.mkdir(parents=True)
        config_file = config_dir / "config.yaml"
        config_file.write_text("control_mode: FIFO\n")
        provider = FileConfigurationProvider(config_file)

        result1 = await provider.load()
        assert result1.control_mode == ControlMode.FIFO

        config_file.write_text("control_mode: VOTING\n")
        result2 = await provider.reload()
        assert result2.control_mode == ControlMode.VOTING

    async def test_reload_same_as_load(self, config_dir: Path) -> None:
        config_dir.mkdir(parents=True)
        config_file = config_dir / "config.yaml"
        config_file.write_text("control_mode: VOTING\nvoting_interval: 45\n")
        provider = FileConfigurationProvider(config_file)

        load_result = await provider.load()
        reload_result = await provider.reload()

        assert load_result == reload_result
