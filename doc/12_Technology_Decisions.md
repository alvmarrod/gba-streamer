# ADR-0001 – Technology Decisions

**Status:** Accepted

**Date:** 2026-07-18

---

# Purpose

This document records the key technology decisions adopted for the Pokémon Crowd Play project.

Detailed implementation is described in the HLD and LLD. This ADR only records **what** was chosen and **why**.

---

# Decision Log

| Topic | Decision | Alternatives Considered | Rationale |
|--------|----------|-------------------------|-----------|
| Architecture | Clean Architecture | Hexagonal, Layered | Clear separation of business logic and infrastructure, high testability and maintainability. |
| Language | Python 3.13 | Go, Rust | Excellent ecosystem compatibility with PyBoy, aiortc and asyncio. |
| Concurrency | asyncio | Threads, multiprocessing | Single-process asynchronous architecture minimizes resource usage on Raspberry Pi. |
| Web Framework | aiohttp | FastAPI, Starlette, Quart | Lightweight, mature asyncio support and seamless WebRTC integration. |
| Emulator | PyBoy | SameBoy, mGBA | Native Python API, ARM compatibility and active maintenance. |
| Streaming | aiortc | Janus, mediasoup, GStreamer | Embedded WebRTC implementation avoids additional infrastructure and simplifies deployment. |
| User Interface | Telegram Mini App | Inline Mode, Bot Commands, External Website | Integrated experience combining controls and live video inside Telegram. |
| Video Transport | WebRTC | MJPEG, HLS, RTMP, WebSocket | Lowest latency suitable for collaborative gameplay. |
| Communication | HTTP + WebRTC | WebSocket-only | Clear separation between control plane (HTTP) and media plane (WebRTC). |
| Dependency Injection | Constructor Injection | Service Locator, Global State | Explicit dependencies, easier testing and improved maintainability. |
| Persistence | Emulator Save Files | Database, Event Sourcing | Emulator state is the single source of truth; additional persistence is unnecessary. |
| Save Storage | Filesystem (Bind Mount) | Database, Object Storage | Simple, portable and Docker-friendly. |
| Configuration | YAML + Environment Variables | JSON, TOML, INI | Human-readable configuration with environment overrides. |
| Scheduler | Internal asyncio Scheduler | APScheduler, Celery | Minimal dependencies and deterministic execution within a single process. |
| Logging | Structured Logging | Plain text logs | Better filtering, aggregation and observability. |
| Metrics | Internal Metrics Publisher | Prometheus client only | Keeps monitoring implementation replaceable behind a Port. |
| Containerization | Docker Compose | Kubernetes | Simpler deployment and appropriate for Raspberry Pi scale. |
| Reverse Proxy | Existing Nginx | Embedded HTTP server only | Reuse existing infrastructure and TLS termination. |
| Proxy Integration | Existing Telegram Proxy | Direct Telegram Bot API | Preserves current architecture and centralizes Telegram integration. |
| Control Modes | FIFO and Voting | FIFO only, Voting only | Runtime-selectable strategy allows experimentation without code changes. |
| Autosave Interval | 15 seconds | Manual only, longer intervals | Good balance between resilience and I/O overhead. |
| Runtime Model | Single Process | Microservices | Lower latency, lower memory footprint and simpler deployment. |

---

# Architectural Principles

The following principles guided every technology decision:

- Keep the architecture simple.
- Prefer a single process whenever practical.
- Minimize memory usage.
- Minimize external infrastructure.
- Keep business logic framework-independent.
- Favor explicit dependencies.
- Optimize for Raspberry Pi deployment.
- Design for deterministic behavior.
- Prefer composition over inheritance.
- Keep infrastructure replaceable through Ports.

---

# Deferred Decisions

The following topics are intentionally postponed until required:

- Authentication beyond Telegram validation.
- Horizontal scaling.
- Multiple concurrent game sessions.
- Database persistence.
- Distributed scheduling.
- External metrics backend.
- Replay system.
- Spectator overlays.
- Audio streaming.
- Multi-emulator support.

---

# Decision Review Policy

Technology decisions should only be revisited when one of the following conditions applies:

- A functional requirement changes.
- Performance goals cannot be met.
- Maintenance cost becomes unacceptable.
- A chosen dependency is no longer maintained.
- Security requirements change significantly.

Otherwise, decisions recorded in this document remain valid for the lifetime of the project.

---

# Related Documents

- High-Level Design (HLD)
- Low-Level Design (LLD)
- Repository Blueprint & Development Guidelines