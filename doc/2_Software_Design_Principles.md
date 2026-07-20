# Software Design Principles

## 1. Purpose

This document defines the software design principles that govern the implementation of the project. These principles are intentionally independent of any specific technology or framework and must be respected throughout the lifetime of the project.

Their purpose is to ensure that the codebase remains maintainable, testable, extensible and easy to reason about as new features are added.

---

# 2. Architectural Principles

## 2.1 Clean Architecture

The project follows a strict **Clean Architecture** approach.

Dependencies always point towards the Domain layer.

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

### Rules

- Presentation depends on Application.
- Application depends on Domain.
- Infrastructure depends on Domain and Application interfaces.
- Domain never depends on any other layer.

The Domain layer must remain completely independent from implementation details.

---

## 2.2 Domain First

The business domain is the center of the application.

All implementation decisions must adapt to the domain model, never the opposite.

Technologies such as:

- Telegram
- PyBoy
- aiortc
- aiohttp
- Docker
- JSON
- HTTP
- WebSocket

are considered implementation details.

Replacing any of these technologies must not require modifications to the Domain layer.

---

## 2.3 Single Aggregate Root

The system contains a single Aggregate Root.

```text
GameSession
```

All mutable game state belongs to a GameSession instance.

Examples include:

- Connected players
- Input queue
- Session configuration
- Current vote
- Metrics
- Save metadata

No mutable business state exists outside the aggregate.

---

## 2.4 Rich Domain Model

Entities are responsible for protecting their own invariants.

The application layer coordinates workflows but never manipulates the internal state of an entity directly.

Preferred:

```python
session.submit_input(...)
session.connect_player(...)
session.change_control_mode(...)
```

Avoid:

```python
session.input_queue.enqueue(...)
session.metrics.total_inputs += 1
```

Only the aggregate root is responsible for modifying its internal objects.

---

# 3. Application Layer Principles

## 3.1 Small Use Cases

Each use case represents one business action.

Every use case:

- has a single responsibility;
- exposes only one public execution method;
- is fully asynchronous;
- contains orchestration logic only;
- does not contain business rules.

Examples:

- SubmitInputUseCase
- ChangeControlModeUseCase
- AutosaveUseCase
- ConnectPlayerUseCase

---

## 3.2 One Entry Point = One Use Case

Every external interaction must end in exactly one Use Case.

Examples:

```text
REST Endpoint
        │
        ▼
     Use Case
```

```text
WebSocket Message
        │
        ▼
     Use Case
```

```text
Scheduler Task
        │
        ▼
     Use Case
```

Presentation layers never execute business logic directly.

---

## 3.3 Scheduler as an Orchestrator

The Scheduler is intentionally generic.

Its only responsibility is executing scheduled tasks.

It does not implement business logic.

```text
Scheduler
    │
    ▼
Task
    │
    ▼
Use Case
```

Business behaviour always remains inside Use Cases and the Domain.

---

# 4. Domain Modeling Principles

## 4.1 Entities

Entities represent concepts with identity.

Current entities:

- GameSession
- Player

Entities protect their own consistency.

---

## 4.2 Value Objects

Objects without identity are modeled as Value Objects.

Examples:

- SessionId
- PlayerId
- GameInput
- InputQueue
- VoteRound
- VoteResult
- SessionConfiguration
- SaveMetadata
- Metrics
- PlayerStatistics

Value Objects exist only as part of another entity.

---

## 4.3 Domain Services

Complex business rules that do not naturally belong to an Entity are implemented as Domain Services.

Examples:

- VoteResolver
- FIFOResolver
- MetricsCalculator
- SessionValidator

Domain Services should be stateless whenever possible.

---

## 4.4 Domain Isolation

The Domain layer never imports or references:

- infrastructure code;
- frameworks;
- network protocols;
- serialization formats;
- operating system APIs.

The Domain must be executable in complete isolation.

---

# 5. Infrastructure Principles

## 5.1 Replaceable Infrastructure

Infrastructure components are implementations of interfaces defined by the application.

Examples:

- PyBoy Emulator
- aiortc Video Publisher
- File-based Save Repository
- Configuration Provider

Each implementation must be replaceable without affecting business logic.

---

## 5.2 Infrastructure Owns Technology

Infrastructure is responsible for:

- filesystem access;
- emulator interaction;
- WebRTC;
- HTTP;
- WebSocket;
- logging;
- configuration loading;
- monitoring.

No technology-specific code is allowed outside this layer.

---

# 6. Presentation Principles

Presentation only converts external communication into application requests.

Responsibilities include:

- HTTP routing
- WebSocket handling
- DTO validation
- Request parsing
- Response serialization

Presentation never contains business rules.

---

# 7. Asynchronous Execution

The application is fully asynchronous.

All long-running operations execute using asyncio.

Examples:

- WebSocket server
- REST server
- Scheduler
- Emulator loop
- Autosave
- Voting timer
- Metrics collection
- WebRTC publishing

Threads should only be introduced when strictly required by third-party libraries.

---

# 8. State Management

The project avoids global mutable state.

Business state belongs exclusively to GameSession.

Infrastructure services should remain stateless whenever possible.

Configuration is immutable during execution unless explicitly reloaded through a Use Case.

---

# 9. Dependency Rules

Allowed dependency direction:

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

Forbidden examples:

- Domain → Infrastructure
- Domain → Presentation
- Application → Presentation
- Presentation → Infrastructure (bypassing Application)

---

# 10. Testability

Every layer must be independently testable.

The Domain layer should be testable without:

- Telegram
- WebRTC
- PyBoy
- aiohttp
- Docker
- Filesystem

Application tests should use mocked interfaces.

Infrastructure should be tested separately.

---

# 11. Extensibility

Future features should require extending the system rather than modifying existing components.

Examples include:

- Additional control modes
- Alternative emulators
- Multiple game sessions
- Different persistence mechanisms
- Alternative streaming technologies

The architecture should support these changes through composition and interface implementations rather than invasive modifications.

---

# 12. Development Philosophy

The implementation should prioritize:

1. Correctness
2. Simplicity
3. Readability
4. Testability
5. Performance

Performance optimizations should only be introduced when supported by measurable evidence.

Premature optimization should be avoided.

---

# 13. Summary

The project is built around four core principles:

- **The Domain is the source of truth.**
- **Infrastructure is replaceable.**
- **Business logic lives inside the Domain.**
- **Application coordinates, Presentation communicates, Infrastructure implements.**

These principles form the foundation for the Low-Level Design (LLD) and should guide every implementation decision throughout the project.