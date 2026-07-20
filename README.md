# gba-streamer

A collaborative real-time gaming platform embedded inside Telegram.

Players connect through a Telegram Mini App to watch live gameplay via WebRTC
while sending controls through a WebSocket-based virtual controller. The
backend runs headlessly on ARM hardware, coordinating the emulator, input
strategies and video streaming in a single modular monolith.

## Tech Stack

- **Language:** Python 3.14+
- **HTTP / WebSocket:** aiohttp
- **Video streaming:** aiortc (WebRTC)
- **Emulator:** PyBoy
- **Linting / Formatting:** ruff
- **Type checking:** mypy
- **Testing:** pytest
- **Package management:** uv
- **Containerization:** Docker Compose

## Getting Started

```bash
# Install dependencies
uv sync

# Install pre-commit hooks
pre-commit install

# Run the application
uv run python -m consumer.main

# Run tests
uv run pytest

# Lint and format
uv run ruff check src/ tests/
uv run ruff format src/ tests/

# Type check
uv run mypy src/ tests/
```

## Architecture

The project follows Clean Architecture with strict layer dependency rules.
Full architecture documentation is available in the [`doc/`](doc/) directory.

## License

MIT
