# Part 8 – Dependency DAG & Development Roadmap

---

# 1. Overview

This section defines the implementation dependencies of the project.

Its purpose is to:

- prevent circular dependencies;
- define the recommended implementation order;
- identify parallel development opportunities;
- provide a roadmap from an empty repository to a fully working system.

The dependency graph is intentionally acyclic.

---

# 2. Layer Dependency DAG

The highest-level dependency graph is:

```text
Presentation
        │
        ▼
Application
        │
        ▼
Domain
        ▲
        │
Infrastructure
```

The Domain layer has no external dependencies.

---

# 3. Package Dependency DAG

```text
presentation
        │
        ▼
application
   ┌────┴────┐
   ▼         ▼
domain     ports
             ▲
             │
      infrastructure
```

Rules:

- `presentation` depends only on `application`.
- `application` depends on `domain` and `ports`.
- `domain` depends only on itself.
- `infrastructure` implements `ports`.
- `ports` never depend on infrastructure.

---

# 4. Domain Dependency DAG

```text
Enums
   │
   ▼
Value Objects
   │
   ▼
Composed Domain Objects
   │
   ▼
Entities
   │
   ▼
Domain Services
   │
   ▼
Exceptions
```

Recommended implementation order:

1. Enums
2. Value Objects
3. Composed Domain Objects
4. Entities
5. Domain Services
6. Exceptions

---

# 5. Application Dependency DAG

```text
DTO
    │
    ▼
Mappers
    │
    ▼
Ports
    │
    ▼
Use Cases
    │
    ▼
Scheduler
```

Recommended implementation order:

1. DTOs
2. Mappers
3. Ports
4. Use Cases
5. Scheduler

---

# 6. Infrastructure Dependency DAG

```text
Configuration
      │
      ▼
PyBoyAdapter
      │
      ├─────────────┐
      ▼             ▼
Framebuffer     Snapshot
      │
      ▼
AiortcVideoPublisher
      │
      ▼
Persistence

      ▼

Monitoring
```

Recommended implementation order:

1. Configuration
2. PyBoyAdapter
3. Snapshot support
4. Framebuffer support
5. Save repository
6. aiortc publisher
7. Logging
8. Metrics

---

# 7. Presentation Dependency DAG

```text
Static Assets
      │
      ▼
Telegram WebApp
      │
      ▼
Middleware
      │
      ▼
Controllers
      │
      ▼
DTO
      │
      ▼
Use Cases
```

Recommended implementation order:

1. Middleware
2. Controllers
3. WebApp
4. Static assets

---

# 8. Runtime Dependency DAG

```text
Configuration
      │
      ▼
Infrastructure
      │
      ▼
GameSession
      │
      ▼
Application
      │
      ▼
Presentation
      │
      ▼
Scheduler
      │
      ▼
Running System
```

---

# 9. Class Dependency Graph (High Level)

```text
                 GameSession
                      │
        ┌─────────────┼─────────────┐
        ▼             ▼             ▼
 PlayerManager   InputQueue    SessionStateMachine
        │             │
        ▼             ▼
     Player       GameInput
        │
        ▼
 PlayerStatistics
```

---

```text
SubmitInputUseCase
        │
        ▼
GameSessionProvider
        │
        ▼
GameSession
        │
        ▼
EmulatorControlPort
```

---

```text
TickEmulatorUseCase
        │
        ├──────────────► EmulatorControlPort
        │
        └──────────────► VideoPublisherPort
```

---

# 10. Parallel Development Opportunities

After the Domain layer is complete, the project can be developed in parallel.

## Team A

Application layer:

- DTOs
- Ports
- Mappers
- Use Cases

---

## Team B

Infrastructure:

- PyBoy adapter
- Save repository
- Configuration
- Logging

---

## Team C

Streaming:

- aiortc
- WebRTC signalling
- Video publication

---

## Team D

Presentation:

- HTTP API
- Telegram WebApp
- Middleware

---

# 11. Recommended Development Roadmap

## Phase 1 — Foundation

- Repository structure
- Tooling
- Configuration
- Logging
- CI

---

## Phase 2 — Domain

- Enums
- Value Objects
- Composed Objects
- Entities
- Domain Services

---

## Phase 3 — Application

- Ports
- DTOs
- Mappers
- Use Cases
- Scheduler

---

## Phase 4 — Emulator

- PyBoy integration
- Snapshot support
- Input execution

---

## Phase 5 — Streaming

- aiortc
- Signalling
- Video publication

---

## Phase 6 — Presentation

- Internal API
- Telegram WebApp
- Static assets

---

## Phase 7 — Runtime

- Dependency injection
- Bootstrap
- Health checks
- Autosave

---

## Phase 8 — Validation

- Unit tests
- Integration tests
- End-to-End tests
- Simulation tests
- Reliability tests

---

# 12. Milestones

| Milestone | Expected Result |
|-----------|-----------------|
| M1 | Domain fully implemented |
| M2 | Application layer operational |
| M3 | Emulator executes inputs |
| M4 | WebRTC video available |
| M5 | Telegram WebApp controls the emulator |
| M6 | Autosave and restore operational |
| M7 | Full end-to-end gameplay |
| M8 | Production-ready system |

---

# 13. Architecture Validation Checklist

Before considering the implementation complete, verify:

- [ ] No circular dependencies exist.
- [ ] Domain contains no infrastructure imports.
- [ ] Every infrastructure adapter implements one or more Ports.
- [ ] Every controller invokes exactly one Use Case.
- [ ] Every business operation starts from GameSession.
- [ ] Scheduler contains no business logic.
- [ ] WebRTC operates independently from HTTP request processing.
- [ ] Autosave survives application restart.
- [ ] Unit tests pass without infrastructure.
- [ ] Integration tests validate every adapter.
- [ ] End-to-End gameplay is fully functional.
- [ ] Simulation tests validate concurrent user interaction.

---

# End of Low-Level Design

This document defines the complete software architecture for the Pokémon Yellow Crowd Play platform.

Any implementation should conform to the dependency rules, architectural boundaries and development roadmap described throughout this document.