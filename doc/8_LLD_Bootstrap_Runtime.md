# Part 6 – Bootstrap & Runtime

---

# 1. Overview

The Bootstrap layer is responsible for assembling the complete application.

It acts as the Composition Root of the system.

Responsibilities include:

- Loading configuration
- Creating infrastructure adapters
- Wiring dependencies
- Creating Application services
- Creating the HTTP server
- Starting scheduled tasks
- Managing application lifecycle

Business logic never belongs in the Bootstrap layer.

---

# 2. Runtime Components

The runtime consists of the following major components.

```text
Configuration

↓

Infrastructure Adapters

↓

Application Services

↓

Presentation Layer

↓

Scheduler

↓

Running Application
```

Each component is initialized exactly once.

---

# 3. Startup Sequence

Application startup follows the sequence below.

```text
Load Configuration

↓

Initialize Logger

↓

Initialize Metrics

↓

Create PyBoyAdapter

↓

Create FileSaveRepository

↓

Create ConfigurationProvider

↓

Create AiortcVideoPublisher

↓

Restore Last Save

↓

Create GameSession

↓

Create GameSessionProvider

↓

Create Use Cases

↓

Create Scheduler

↓

Create HTTP Server

↓

Register Routes

↓

Register WebRTC Signalling

↓

Start Scheduler

↓

Start HTTP Server

↓

Application Running
```

Startup fails immediately if any mandatory dependency cannot be initialized.

---

# 4. Dependency Injection

Dependency injection is constructor-based.

The Composition Root owns every object instance.

Dependencies are assembled from the outside inward.

Example dependency graph:

```text
main.py

│

├── Configuration

├── LoggerAdapter

├── MetricsPublisher

├── PyBoyAdapter

├── FileSaveRepository

├── AiortcVideoPublisher

├── GameSession

├── GameSessionProvider

├── Use Cases

├── Scheduler

└── aiohttp Application
```

No object creates its own dependencies.

---

# 5. Runtime Object Graph

```text
                    main.py
                       │
                       ▼
             Dependency Injection
                       │
      ┌────────────────┴────────────────┐
      ▼                                 ▼
Infrastructure                  Application
      │                                 │
      ▼                                 ▼
 PyBoyAdapter                 GameSessionProvider
      │                                 │
      ▼                                 ▼
AiortcVideoPublisher             Use Cases
      │                                 │
      └──────────────┬──────────────────┘
                     ▼
               aiohttp Server
                     │
                     ▼
             Telegram WebApp
```

The object graph remains static after startup.

---

# 6. Scheduler Initialization

The Scheduler is created during startup.

Registered tasks include:

```text
TickTask

AutosaveTask

ResolveVoteTask

MetricsTask

HealthCheckTask
```

Tasks are started after the HTTP server is fully initialized.

---

# 7. WebRTC Initialization

The aiortc components are initialized during application startup.

Responsibilities include:

- PeerConnection management
- ICE configuration
- Signalling endpoint registration
- Video publisher initialization

No PeerConnection exists until a client initiates a session.

---

# 8. GameSession Initialization

The GameSession Aggregate is initialized during startup.

Initialization sequence:

```text
Create Aggregate

↓

Load Configuration

↓

Restore Save (if available)

↓

Set Initial State

↓

Expose through GameSessionProvider
```

The Aggregate remains alive for the entire application lifetime.

---

# 9. Shutdown Sequence

Graceful shutdown follows the sequence below.

```text
Stop accepting HTTP requests

↓

Stop Scheduler

↓

Close WebRTC PeerConnections

↓

Create Final Snapshot

↓

Persist Save File

↓

Flush Metrics

↓

Flush Logs

↓

Release PyBoy

↓

Shutdown Complete
```

Shutdown must preserve game progress whenever possible.

---

# 10. Failure Handling

Failures during startup are fatal.

Failures during runtime are isolated whenever possible.

Examples:

- Failed save → log error, continue execution.
- Lost WebRTC peer → disconnect peer only.
- Invalid request → reject request.
- Scheduler task failure → log and retry according to policy.

Business state must remain consistent.

---

# 11. Health Management

Health status is exposed through the HealthCheck Use Case.

Health indicators include:

- HTTP server
- Scheduler
- Emulator
- Persistence
- Streaming

Health reporting remains read-only.

---

# 12. Runtime Configuration

Configuration is loaded during startup.

Supported configuration domains include:

```text
Server

Scheduler

Emulator

Streaming

Persistence

Logging

Metrics
```

Runtime reload is supported only for explicitly reloadable settings.

---

# 13. Runtime Dependency DAG

```text
Configuration

↓

Logger

↓

Metrics

↓

Infrastructure

↓

GameSession

↓

Application

↓

Presentation

↓

Scheduler

↓

Running System
```

The runtime graph contains no cycles.

---

# 14. Implementation Rules

- `main.py` acts exclusively as the Composition Root.
- All dependencies are injected through constructors.
- Heavy resources are created exactly once.
- Runtime state is owned exclusively by the Domain.
- Infrastructure adapters remain singleton unless explicitly required otherwise.
- Scheduler starts only after successful initialization.
- Graceful shutdown shall preserve emulator state whenever possible.

