# Part 7 – Testing Strategy

---

# 1. Overview

Testing follows the same architectural boundaries defined throughout this document.

The testing strategy is designed to:

- Validate business correctness
- Verify infrastructure integrations
- Ensure end-to-end functionality
- Prevent architectural regressions

Tests shall be deterministic, repeatable and independent whenever possible.

---

# 2. Test Repository Structure

```text
tests/
│
├── unit/
│
│   ├── domain/
│   ├── application/
│   └── presentation/
│
├── integration/
│
│   ├── emulator/
│   ├── streaming/
│   ├── persistence/
│   ├── scheduler/
│   └── api/
│
├── e2e/
│
│   ├── gameplay/
│   ├── voting/
│   ├── save_restore/
│   └── webapp/
│
├── fixtures/
│
├── resources/
│
└── conftest.py
```

---

# 3. Testing Pyramid

The project follows a classic testing pyramid.

```text
             End-to-End

          Integration Tests

             Unit Tests
```

The majority of tests shall be Unit Tests.

---

# 4. Unit Tests

Unit Tests validate individual software components in isolation.

No external dependency shall be required.

---

## Domain

Domain tests validate:

- Entities
- Value Objects
- Composed Domain Objects
- Domain Services
- Business Exceptions

No Infrastructure component shall be involved.

---

## Application

Application tests validate:

- Use Cases
- Scheduler
- Mappers

Ports shall be replaced by test doubles.

---

## Presentation

Presentation tests validate:

- Request validation
- DTO mapping
- Error translation

Business logic shall be mocked.

---

# 5. Integration Tests

Integration Tests validate interactions with concrete Infrastructure.

---

## Emulator

Validate:

- PyBoy initialization
- Input execution
- Frame generation
- Save creation
- Save restoration

---

## Streaming

Validate:

- WebRTC signalling
- Peer connection establishment
- Video publication
- Multiple simultaneous viewers

---

## Persistence

Validate:

- Save creation
- Save loading
- Missing save handling
- Filesystem errors

---

## Scheduler

Validate:

- Periodic execution
- Task isolation
- Recovery after task failures

---

## API

Validate:

- Endpoint routing
- Serialization
- Request lifecycle
- Error handling

---

# 6. End-to-End Tests

End-to-End tests validate complete user workflows.

---

## Gameplay

Scenario:

```text
Telegram WebApp

↓

Player Input

↓

Backend

↓

Emulator

↓

Updated Video
```

---

## Voting

Scenario:

```text
Multiple Players

↓

Vote Window

↓

Vote Resolution

↓

Input Execution
```

---

## Save & Restore

Scenario:

```text
Running Session

↓

Autosave

↓

Shutdown

↓

Restart

↓

State Restored
```

---

## Streaming

Scenario:

```text
Viewer Connects

↓

WebRTC

↓

Live Video

↓

Viewer Disconnects
```

---

# 7. Test Fixtures

Reusable fixtures include:

- Test GameSession
- Fake Configuration
- Fake Save
- Fake Metrics
- Fake Player
- Sample ROM

Fixtures remain deterministic.

---

# 8. Test Doubles

Application tests replace Ports using test doubles.

Examples:

```text
FakeGameSessionProvider

FakeEmulatorControlPort

FakeFramebufferProviderPort

FakeSnapshotPort

FakeVideoPublisherPort

FakeSaveRepositoryPort

FakeLoggerPort

FakeMetricsPublisherPort
```

No Infrastructure implementation shall be used during Unit Tests.

---

# 9. Coverage Strategy

Coverage priorities:

1. Domain
2. Application
3. Infrastructure
4. Presentation

Business correctness has priority over framework coverage.

---

# 10. Performance Tests

Performance tests validate:

- Tick execution frequency
- Input throughput
- Voting throughput
- Autosave duration
- Startup time
- Memory consumption

Performance tests are not part of the default CI pipeline.

---

# 11. Reliability Tests

Long-running tests validate:

- 24-hour execution
- Continuous streaming
- Repeated save/restore
- Memory stability
- Scheduler stability

These tests may execute independently from the standard test suite.

---

# 12. Test Dependency DAG

```text
Unit Tests

↓

Integration Tests

↓

End-to-End Tests

↓

Performance Tests

↓

Reliability Tests
```

Higher-level tests assume lower-level tests already pass.

---

# 13. Implementation Rules

- Tests shall remain deterministic.
- Unit Tests shall never require network access.
- Unit Tests shall never access the filesystem.
- Integration Tests shall isolate external dependencies.
- End-to-End tests shall exercise complete workflows.
- Test doubles shall implement the same Ports as production adapters.
- Every bug fix shall include a regression test.
- New functionality shall include corresponding tests.
