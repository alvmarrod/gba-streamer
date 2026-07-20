from __future__ import annotations

import os
from pathlib import Path

from aiohttp import web  # type: ignore[import-untyped]

from consumer.bootstrap import create_app


def main() -> None:
    config_path = Path(os.environ.get("CONFIG_PATH", "config/gba-streamer.yaml"))
    rom_path = Path(os.environ.get("ROM_PATH", "roms/pokemon_yellow.gb"))
    save_dir = Path(os.environ.get("SAVE_DIR", "saves/"))

    app = create_app(config_path, rom_path, save_dir)

    host = os.environ.get("HOST", "0.0.0.0")
    port = int(os.environ.get("PORT", "8080"))

    web.run_app(app, host=host, port=port)


if __name__ == "__main__":
    main()
