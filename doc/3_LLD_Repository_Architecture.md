# Pokémon Yellow Crowd Play
## Low-Level Design (LLD)

**Version:** 1.0  
**Status:** Draft  
**Authors:** Project Team

---

# Part 1 – Repository Architecture

---

# 1. Introduction

## 1.1 Purpose

This document describes the low-level software design of the Pokémon Yellow Crowd Play platform.

The purpose of this document is to define the complete internal software architecture, including:

- Repository organization
- Package hierarchy
- Module responsibilities
- Class organization
- Dependency rules
- Internal interfaces
- Component interactions

Unlike the High-Level Design (HLD), this document focuses on implementation details while remaining independent from the source code.

---

## 1.2 Scope

This document covers the implementation of the Crowd Play platform composed of:

- Telegram WebApp backend
- Emulator control
- WebRTC streaming
- Session management
- Player interaction
- Internal REST API
- Scheduler
- Persistence
- Monitoring

Infrastructure external to the project (Telegram Bot Proxy, Docker Compose, Nginx, etc.) is considered out of scope except where integration points are required.

---

# 2. Repository Structure

## 2.1 Repository Philosophy

The repository follows a strict Clean Architecture.

The software is organized by architectural responsibility rather than by feature.

```text
Presentation
Application
Domain
Infrastructure
```

Every package belongs to exactly one architectural layer.

No module should mix responsibilities.

---

## 2.2 Root Directory Layout

```text
pokemon-yellow-crowdplay/
│
├── src/
│
├── tests/
│
├── docs/
│
├── saves/
│
├── roms/
│
├── config/
│
├── scripts/
│
│
├── Dockerfile
├── docker-compose.yml
├── pyproject.toml
├── README.md
└── LICENSE
```

---

## 2.3 Root Directory Responsibilities

| Directory | Responsibility |
|------------|----------------|
| src | Application source code |
| tests | Unit, integration and end-to-end tests |
| docs | Architecture documentation |
| saves | Emulator save files (bind mount) |
| roms | Game ROMs (bind mount) |
| config | Runtime configuration |
| scripts | Utility and maintenance scripts |

---

# 3. Source Code Layout

The application source code is organized into five top-level packages.

```text
src/
│
├── presentation/
├── application/
├── domain/
├── infrastructure/
├── shared/
│
└── main.py
```

---

# 4. Layer Responsibilities

---

## 4.1 Domain

The Domain layer contains all business rules.

Responsibilities include:

- Domain entities
- Value objects
- Domain services
- Business validation
- Domain exceptions

The Domain layer has no knowledge of infrastructure or frameworks.

Allowed dependencies:

```text
None
```

---

## 4.2 Application

The Application layer coordinates business operations.

Responsibilities include:

- Use Cases
- DTOs
- Interfaces (Ports)
- Scheduler

Business rules remain inside the Domain.

Allowed dependencies:

```text
Application
        │
        ▼
Domain
```

---

## 4.3 Infrastructure

Infrastructure contains all technology-specific implementations.

Examples include:

- PyBoy
- aiortc
- Filesystem persistence
- Configuration loading
- Logging
- Monitoring

Allowed dependencies:

```text
Infrastructure
        │
        ├────────────► Domain
        │
        └────────────► Application Interfaces
```

---

## 4.4 Presentation

Presentation exposes the application externally.

Responsibilities include:

- HTTP endpoints
- WebSocket endpoints
- DTO validation
- Request parsing
- Response serialization

Presentation never executes business logic directly.

Allowed dependencies:

```text
Presentation
        │
        ▼
Application
```

---

## 4.5 Shared

Shared contains generic utilities that are not business-specific.

Examples:

- Constants
- Generic helpers
- Common types

Shared must never contain business logic.

---

# 5. Repository Tree

The repository tree below represents the intended final structure.

```text
src/
│
├── application/
│   ├── dto/
│   ├── interfaces/
│   ├── mappers/
│   ├── scheduler/
│   └── use_cases/
│
├── domain/
│   ├── entities/
│   ├── enums/
│   ├── exceptions/
│   ├── services/
│   └── value_objects/
│
├── infrastructure/
│   ├── configuration/
│   ├── emulator/
│   ├── monitoring/
│   ├── persistence/
│   ├── streaming/
│   └── telegram/
│
├── presentation/
│   ├── api/
│   ├── middleware/
│   ├── websocket/
│   └── webapp/
│
├── shared/
│
└── main.py
```

---

# 6. Dependency Rules

The following dependency rules are mandatory.

---

## Rule 1

Dependencies always point inward.

```text
Presentation

↓

Application

↓

Domain
```

Infrastructure depends on interfaces defined by the Application layer.

---

## Rule 2

The Domain layer must never import:

- aiohttp
- aiortc
- PyBoy
- Telegram
- JSON
- HTTP
- Docker

---

## Rule 3

Presentation never accesses Infrastructure directly.

Every request must pass through a Use Case.

---

## Rule 4

Infrastructure never exposes implementation classes outside its package.

Communication always occurs through interfaces.

---

## Rule 5

Shared contains only implementation-independent utilities.

Business concepts belong exclusively to Domain.

---

# 7. High-Level Module Diagram

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

---

# 8. Initial Dependency DAG

The repository dependency graph is intentionally acyclic.

```text
                shared
                   │
                   ▼
                domain
                   │
                   ▼
             application
                   ▲
                   │
          infrastructure
                   ▲
                   │
             presentation
                   │
                   ▼
                main.py
```

No dependency cycles are permitted.

Every new module introduced during development must preserve this graph.

---

# 9. Development Order

The recommended implementation order is derived directly from the dependency graph.

```text
shared
    │
    ▼
domain
    │
    ▼
application
    │
    ▼
infrastructure
    │
    ▼
presentation
    │
    ▼
bootstrap (main.py)
```

This order minimizes mocking requirements and ensures each layer can be validated before introducing the next.

---

# 10. Implementation Notes

The following implementation guidelines apply to the entire repository.

- All public application methods shall be asynchronous.
- Dependency injection shall be constructor-based.
- Business rules belong exclusively to the Domain layer.
- Infrastructure implementations shall remain replaceable.
- Composition shall be preferred over inheritance.
- Circular dependencies are forbidden.
- Every external interaction shall terminate in exactly one Use Case.
- Mutable business state shall exist only within the `GameSession` aggregate.
