from __future__ import annotations

import json
import os

from aiortc import RTCConfiguration, RTCIceServer  # type: ignore[import-untyped]

_DEFAULT_STUN = RTCConfiguration(
    iceServers=[RTCIceServer(urls=["stun:stun.l.google.com:19302"])]
)


class IceConfigProvider:
    def __init__(self) -> None:
        raw = os.environ.get("ICE_SERVERS", "")
        self._config = self._parse(raw)

    @property
    def configuration(self) -> RTCConfiguration:
        return self._config

    @staticmethod
    def _parse(raw: str) -> RTCConfiguration:
        if not raw:
            return _DEFAULT_STUN
        try:
            servers = json.loads(raw)
            ice_servers = [
                RTCIceServer(
                    urls=s.get("urls", []),
                    username=s.get("username"),
                    credential=s.get("credential"),
                )
                for s in servers
            ]
            return RTCConfiguration(iceServers=ice_servers)
        except json.JSONDecodeError, TypeError, KeyError:
            return _DEFAULT_STUN
