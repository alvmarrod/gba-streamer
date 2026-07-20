from __future__ import annotations

import json
import os
from unittest.mock import patch

from consumer.infrastructure.streaming.ice_config import IceConfigProvider


def _assert_servers_not_none(config: IceConfigProvider) -> None:
    assert config.configuration.iceServers is not None


class TestIceConfigProvider:
    def test_default_stun_when_env_empty(self) -> None:
        with patch.dict(os.environ, {}, clear=True):
            config = IceConfigProvider()
            _assert_servers_not_none(config)
            servers = config.configuration.iceServers
            assert servers is not None  # for mypy narrow, though redundant
            assert len(servers) == 1
            assert servers[0].urls == ["stun:stun.l.google.com:19302"]

    def test_default_stun_when_env_blank(self) -> None:
        with patch.dict(os.environ, {"ICE_SERVERS": ""}, clear=True):
            config = IceConfigProvider()
            _assert_servers_not_none(config)
            servers = config.configuration.iceServers
            assert servers is not None
            assert "stun:stun.l.google.com:19302" in servers[0].urls

    def test_custom_stun_from_env(self) -> None:
        raw = json.dumps([{"urls": ["stun:custom.stun.com:3478"]}])
        with patch.dict(os.environ, {"ICE_SERVERS": raw}, clear=True):
            config = IceConfigProvider()
            _assert_servers_not_none(config)
            servers = config.configuration.iceServers
            assert servers is not None
            assert len(servers) == 1
            assert servers[0].urls == ["stun:custom.stun.com:3478"]

    def test_turn_with_credentials(self) -> None:
        raw = json.dumps(
            [
                {"urls": ["stun:stun.l.google.com:19302"]},
                {
                    "urls": ["turn:turn.example.com:3478"],
                    "username": "user",
                    "credential": "pass",
                },
            ]
        )
        with patch.dict(os.environ, {"ICE_SERVERS": raw}, clear=True):
            config = IceConfigProvider()
            _assert_servers_not_none(config)
            servers = config.configuration.iceServers
            assert servers is not None
            assert len(servers) == 2
            assert servers[1].username == "user"
            assert servers[1].credential == "pass"

    def test_invalid_json_falls_back_to_default(self) -> None:
        with patch.dict(os.environ, {"ICE_SERVERS": "not-json"}, clear=True):
            config = IceConfigProvider()
            _assert_servers_not_none(config)
            servers = config.configuration.iceServers
            assert servers is not None
            assert "stun.l.google.com" in servers[0].urls[0]

    def test_empty_array_works(self) -> None:
        with patch.dict(os.environ, {"ICE_SERVERS": "[]"}, clear=True):
            config = IceConfigProvider()
            _assert_servers_not_none(config)
            servers = config.configuration.iceServers
            assert servers is not None
            assert len(servers) == 0
