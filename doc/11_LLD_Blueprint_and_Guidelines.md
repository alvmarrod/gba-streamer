# Repository Blueprint & Development Guidelines

Version: 1.0

This document defines the repository structure, coding conventions and development workflow. Detailed architectural decisions are defined in the High-Level Design (HLD) and Low-Level Design (LLD).

---

# 1. Repository Layout

```text
pokemon-crowd-play/
│
├── config/
├── docker/
├── docs/
│   ├── hld/
│   ├── lld/
│   └── blueprint/
├── roms/
├── saves/
├── scripts/
├── src/
├── tests/
│
├── .gitignore
├── .pre-commit-config.yaml
├── docker-compose.yml
├── pyproject.toml
├── README.md
└── uv.lock
```

---

# 2. Source Layout

```text
src/
│
└── consumer/
    │
    ├── application/
    ├── domain/
    ├── infrastructure/
    ├── presentation/
    ├── bootstrap/
    └── main.py
```

Dependency direction:

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

Bootstrap → All
```

---

# 3. Naming Conventions

| Component | Suffix |
|----------|---------|
| Use Case | `UseCase` |
| Port | `Port` |
| Adapter | `Adapter` |
| DTO | `Request` / `Response` |
| Mapper | `Mapper` |
| Entity | none |
| Value Object | none |
| Enum | `Enum` |
| Exception | `Exception` |

---

# 4. Dependency Injection

Rules:

- Constructor Injection only.
- No global state.
- No Service Locator.
- No hidden Singletons.
- `bootstrap/` is the Composition Root.

---

# 5. Configuration

Configuration sources:

1. YAML files
2. Environment variables

Runtime configuration belongs to `config/`.

No hardcoded values.

---

# 6. Tooling

| Tool | Purpose |
|------|---------|
| Python 3.13 | Runtime |
| uv | Package management |
| aiohttp | HTTP server |
| aiortc | WebRTC |
| PyBoy | Emulator |
| pytest | Testing |
| ruff | Linting & formatting |
| mypy | Static typing |
| pre-commit | Git hooks |

---

# 7. Coding Rules

Mandatory rules:

- Full type hints.
- Async-first design.
- Thin controllers.
- Business logic only in Domain.
- One public `execute()` per Use Case.
- Ports define capabilities.
- Adapters implement Ports.
- DTOs are immutable.
- No circular dependencies.
- Logging through `LoggerPort` only.

---

# 8. Testing Rules

Every new feature shall include:

- Unit Tests
- Integration Tests (if Infrastructure changes)
- Regression Tests (for bug fixes)

Tests follow the same architectural boundaries as production code.

---

# 9. Docker Rules

One responsibility per container.

Current services:

- Consumer
- (Existing Proxy)
- (Existing Nginx)

Persistent volumes:

- `roms/`
- `saves/`

Health checks enabled.

Restart policy enabled.

---

# 10. Git Workflow

- Small commits.
- One logical change per commit.
- Pull Requests required.
- `main` always deployable.

Commit style:

```text
feat:
fix:
refactor:
docs:
test:
chore:
```

---

# 11. Definition of Done

A task is complete when:

- Architecture respected.
- Tests pass.
- Ruff passes.
- Mypy passes.
- Documentation updated if required.
- No TODOs introduced.
- No dependency rule violated.

---

# 12. First Implementation Order

1. Repository
2. Tooling
3. Domain
4. Application
5. Infrastructure
6. Presentation
7. Bootstrap
8. Docker
9. Testing
10. End-to-End validation