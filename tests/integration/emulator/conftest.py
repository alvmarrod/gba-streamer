from __future__ import annotations

import os
from pathlib import Path

import pytest

_RESOURCES_DIR = Path(__file__).resolve().parents[2] / "resources"


@pytest.fixture
def rom_path() -> Path:
    env = os.environ.get("GBA_TEST_ROM")
    if env:
        p = Path(env)
        if p.exists():
            return p
        pytest.skip(f"GBA_TEST_ROM points to missing file: {p}")

    matches = sorted(_RESOURCES_DIR.glob("*.gb"))
    if matches:
        return matches[0]

    pytest.skip(
        "No ROM found. Place a .gb file in tests/resources/ "
        "or set the GBA_TEST_ROM environment variable."
    )
