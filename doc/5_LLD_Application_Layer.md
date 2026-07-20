
# Part 3 – Application Layer

---

# 1. Overview

The Application layer coordinates all business operations.

It is responsible for orchestrating interactions between the Presentation layer, the Domain layer and Infrastructure through Ports.

Business rules are never implemented here.

The responsibilities of this layer are:

- Execute business Use Cases
- Coordinate Domain objects
- Access external capabilities through Ports
- Execute scheduled operations
- Convert DTOs into Domain objects
- Convert Domain results into DTOs

The Application layer remains independent from every infrastructure technology.

---

# 2. Package Structure

```text
application/
│
├── dto/
│
├── mappers/
│
├── ports/
│
├── scheduler/
│
└── use_cases/
```

---

# 3. Responsibilities

## DTO

Transport-independent immutable data structures.

Responsibilities:

- carry input data
- carry output data
- isolate Presentation from Domain

DTOs never contain business logic.

---

## Mappers

Responsible for translating between DTOs and Domain objects.

Responsibilities:

```text
DTO

↓

Domain Objects
```

and

```text
Domain Objects

↓

DTO
```

Business logic never belongs inside a Mapper.

---

## Ports

Ports define infrastructure capabilities required by the Application layer.

A Port represents **a capability**, never a concrete implementation.

Multiple Ports may be implemented by the same infrastructure adapter.

---

## Scheduler

Coordinates periodic execution of Use Cases.

The Scheduler is generic and contains no business rules.

---

## Use Cases

Each Use Case represents one business action.

Every Use Case:

- has one responsibility;
- exposes one asynchronous `execute()` method;
- coordinates Domain objects;
- accesses Infrastructure only through Ports.

---

# 4. Ports

---

## GameSessionProvider

Provides access to the active Aggregate Root.

Responsibilities:

```text
getSession() → GameSession
```

The Application layer never owns the session lifecycle.

---

## EmulatorControlPort

Controls emulator execution.

Responsibilities:

```text
executeInput(GameInput)

tick()
```

Application has no knowledge of PyBoy.

---

## FramebufferProviderPort

Provides access to the latest emulator framebuffer.

Responsibilities:

```text
getFramebuffer()
```

The framebuffer format is implementation-defined.

---

## SnapshotPort

Provides snapshot operations.

Responsibilities:

```text
createSnapshot()

restoreSnapshot()
```

Persistence details remain hidden.

---

## VideoPublisherPort

Publishes the latest available video frame.

Responsibilities:

```text
publish()
```

The implementation retrieves the framebuffer internally through its own dependencies.

The Application layer never manipulates image buffers.

---

## SaveRepositoryPort

Persists emulator save data.

Responsibilities:

```text
save()

load()
```

---

## ConfigurationProviderPort

Provides runtime configuration.

Responsibilities:

```text
load()

reload()
```

---

## MetricsPublisherPort

Publishes runtime metrics.

Responsibilities:

```text
publish()
```

The destination is implementation-specific.

---

## LoggerPort

Application logging abstraction.

Responsibilities:

```text
debug()

info()

warning()

error()
```

---

# 5. Use Cases

Every business operation is represented by one Use Case.

---

## Session

```text
StartSessionUseCase

StopSessionUseCase

PauseSessionUseCase

ResumeSessionUseCase

RestoreSessionUseCase
```

---

## Player

```text
ConnectPlayerUseCase

DisconnectPlayerUseCase
```

---

## Gameplay

```text
SubmitInputUseCase

ResolveInputUseCase

TickEmulatorUseCase
```

---

## Voting

```text
ResolveVoteUseCase
```

Voting lifecycle is controlled by scheduled execution.

---

## Save

```text
AutosaveUseCase

ManualSaveUseCase
```

---

## Administration

```text
ChangeControlModeUseCase

ReloadConfigurationUseCase
```

---

## Monitoring

```text
CollectMetricsUseCase

HealthCheckUseCase
```

---

# 6. Scheduler

The Scheduler periodically executes Use Cases.

The Scheduler never contains business rules.

Responsibilities:

- register tasks
- execute tasks
- reschedule tasks
- isolate task failures

---

## Scheduled Tasks

```text
TickTask

AutosaveTask

ResolveVoteTask

MetricsTask

HealthCheckTask
```

Each task invokes exactly one Use Case.

---

# 7. Execution Flow

Every external request follows the same execution pipeline.

```text
Presentation

↓

Mapper

↓

DTO

↓

UseCase

↓

GameSessionProvider

↓

GameSession

↓

Ports

↓

Infrastructure
```

No layer may bypass this execution flow.

---

# 8. Tick Execution Flow

The emulator execution loop follows this sequence.

```text
TickTask

↓

TickEmulatorUseCase

↓

GameSessionProvider

↓

GameSession

↓

EmulatorControlPort.tick()

↓

VideoPublisherPort.publish()
```

The video publisher retrieves the framebuffer internally through the appropriate infrastructure implementation.

Application never accesses framebuffer data.

---

# 9. Use Case Lifecycle

Every Use Case follows the same execution model.

```text
Receive DTO

↓

Validate DTO

↓

Retrieve GameSession

↓

Execute Domain operation

↓

Invoke required Ports

↓

Return DTO
```

Business decisions always remain inside the Domain layer.

---

# 10. Dependency Rules

The Application layer may depend only on:

- Domain
- DTOs
- Mappers
- Ports

The Application layer shall never depend directly on:

- Infrastructure
- Presentation
- Frameworks

---

# 11. Application UML

```text
                    Presentation
                          │
                          ▼
                        DTO
                          │
                          ▼
                      Mapper
                          │
                          ▼
                      UseCase
                          │
                          ▼
                GameSessionProvider
                          │
                          ▼
                    GameSession
                          │
                          ▼
                 Domain Components
                          │
                          ▼
                        Ports
                          │
                          ▼
                  Infrastructure
```

---

# 12. Application Dependency DAG

```text
DTO

↓

Mappers

↓

Ports

↓

UseCases

↓

Scheduler
```

The dependency graph is acyclic.

---

# 13. Implementation Rules

- Every public method shall be asynchronous.
- Every Use Case exposes exactly one public `execute()` method.
- Every Use Case represents one business operation.
- Use Cases interact only with the Aggregate Root.
- Infrastructure capabilities shall always be accessed through Ports.
- DTOs are immutable.
- Mappers contain no business logic.
- Scheduler tasks execute exactly one Use Case.
- Application shall never manipulate framebuffer data directly.

---

# 14. Internal Communication

The only permitted communication paths are:

```text
Presentation

↓

Application

↓

Domain
```

and

```text
Application

↓

Ports

↓

Infrastructure
```

No additional communication paths are permitted.


