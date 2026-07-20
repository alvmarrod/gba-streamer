# Part 4 – Infrastructure Layer

---

# 1. Overview

The Infrastructure layer provides concrete implementations for every capability required by the Application layer.

Its responsibilities include:

- Emulator integration
- Video streaming
- Save persistence
- Configuration loading
- Logging
- Metrics publication

Infrastructure contains no business rules.

Every component implements one or more Application Ports.

---

# 2. Package Structure

```text
infrastructure/
│
├── configuration/
│
├── emulator/
│
├── monitoring/
│
├── persistence/
│
├── streaming/
│
└── telegram/
```

---

# 3. Responsibilities

## Configuration

Provides runtime configuration.

Responsibilities:

- Load configuration
- Reload configuration
- Validate configuration format

---

## Emulator

Provides the concrete emulator implementation.

Responsibilities:

- Execute player inputs
- Advance emulator frames
- Produce framebuffer
- Create emulator snapshots
- Restore emulator snapshots

---

## Streaming

Responsible for video publication.

Responsibilities:

- Capture emulator frames
- Encode video
- Publish WebRTC streams
- Manage Peer Connections

---

## Persistence

Responsible for filesystem persistence.

Responsibilities:

- Store save files
- Load save files

---

## Monitoring

Responsible for operational monitoring.

Responsibilities:

- Logging
- Metrics publication
- Health information

---

# 4. Adapter Overview

Infrastructure consists of the following adapters.

---

## PyBoyAdapter

Implements:

```text
EmulatorControlPort

FramebufferProviderPort

SnapshotPort
```

Responsibilities:

- Own a single PyBoy instance
- Execute Game Boy inputs
- Advance emulator execution
- Produce the current framebuffer
- Generate emulator save states

---

## AiortcVideoPublisher

Implements:

```text
VideoPublisherPort
```

Responsibilities:

- Retrieve framebuffer
- Encode video frames
- Publish WebRTC video
- Manage connected viewers

The framebuffer is obtained through the FramebufferProviderPort.

---

## FileSaveRepository

Implements:

```text
SaveRepositoryPort
```

Responsibilities:

- Read save files
- Write save files

Save location is externally configurable.

---

## FileConfigurationProvider

Implements:

```text
ConfigurationProviderPort
```

Responsibilities:

- Read configuration
- Reload configuration

---

## MetricsPublisher

Implements:

```text
MetricsPublisherPort
```

Responsibilities:

- Export runtime metrics
- Aggregate counters

The export destination is configurable.

---

## LoggerAdapter

Implements:

```text
LoggerPort
```

Responsibilities:

- Debug logging
- Information logging
- Warning logging
- Error logging

---

# 5. Adapter Composition

A single adapter may implement multiple Ports.

Example:

```text
               PyBoyAdapter
                    │
      ┌─────────────┼─────────────┐
      ▼             ▼             ▼

EmulatorControl  Framebuffer   Snapshot
     Port         Provider      Port
```

This minimizes memory usage and avoids synchronization between multiple wrappers around the same emulator instance.

---

# 6. Runtime Object Graph

```text
                    main.py
                       │
                       ▼
               Dependency Injection
                       │
                       ▼
               PyBoyAdapter
                  │    │    │
                  │    │    │
                  ▼    ▼    ▼
 EmulatorControl  Framebuffer  Snapshot
      Port         Provider      Port

                       │

                       ▼

             AiortcVideoPublisher

                       │

                       ▼

                 WebRTC Clients
```

---

# 7. Frame Pipeline

The video generation pipeline follows this sequence.

```text
TickEmulatorUseCase

↓

EmulatorControlPort.tick()

↓

AiortcVideoPublisher.publish()

↓

FramebufferProviderPort.getFramebuffer()

↓

Video Encoder

↓

WebRTC PeerConnection
```

The Application layer never manipulates frame data.

---

# 8. Save Pipeline

```text
AutosaveUseCase

↓

SnapshotPort.createSnapshot()

↓

SaveRepositoryPort.save()

↓

Filesystem
```

Restore follows the reverse direction.

---

# 9. Configuration Pipeline

```text
ConfigurationProvider

↓

Application

↓

SessionConfiguration
```

Infrastructure validates file syntax.

Business validation remains inside the Domain.

---

# 10. Dependency Rules

Infrastructure may depend on:

- Domain
- Application Ports

Infrastructure shall never depend on:

- Presentation
- DTOs
- Use Cases

Infrastructure adapters never communicate directly with each other unless required by composition.

---

# 11. Infrastructure UML

```text
                PyBoyAdapter
             ▲      ▲       ▲
             │      │       │
             │      │       │
 EmulatorControl  Framebuffer  Snapshot
      Port         Provider      Port


        AiortcVideoPublisher
                   ▲
                   │
                   │
          VideoPublisherPort


      FileSaveRepository
               ▲
               │
               │
      SaveRepositoryPort


 FileConfigurationProvider
               ▲
               │
               │
ConfigurationProviderPort


LoggerAdapter
       ▲
       │
       │
 LoggerPort


MetricsPublisher
       ▲
       │
       │
MetricsPublisherPort
```

---

# 12. Infrastructure Dependency DAG

```text
Filesystem

↓

Configuration

↓

PyBoy

↓

Streaming

↓

Monitoring
```

No cyclic dependencies are permitted.

---

# 13. Implementation Rules

- Every adapter implements one or more Ports.
- Adapters remain stateless whenever practical.
- Heavy resources are owned by a single adapter instance.
- Infrastructure never contains business decisions.
- Every adapter shall be replaceable without modifying the Application layer.
- Infrastructure exceptions shall be translated before crossing layer boundaries.

---

# 14. Internal Communication

Infrastructure communicates only through Ports.

The only permitted dependency direction is:

```text
Application

↓

Ports

↓

Infrastructure
```

No adapter may access another adapter through concrete implementations.
