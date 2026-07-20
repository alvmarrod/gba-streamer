
# Part 2 – Domain Layer

---

# 1. Overview

The Domain layer contains the complete business model of the Crowd Play platform.

Its purpose is to encapsulate every business rule while remaining completely independent from infrastructure, frameworks and communication protocols.

The Domain layer defines:

- Business entities
- Value Objects
- Composed Domain Objects
- Domain Services
- Business Exceptions
- Business Enumerations

The Domain layer must compile and execute without knowledge of:

- Telegram
- aiohttp
- aiortc
- PyBoy
- HTTP
- WebSocket
- Filesystem
- Docker
- JSON

---

# 2. Package Structure

```text
domain/
│
├── entities/
│
├── value_objects/
│
├── composed/
│
├── services/
│
├── enums/
│
└── exceptions/
```

---

# 3. Domain Object Classification

The Domain distinguishes three different categories of business objects.

---

## 3.1 Entities

Entities represent business concepts with identity.

Current entities:

- GameSession
- Player

Entities own business behaviour and protect business invariants.

---

## 3.2 Value Objects

Value Objects describe immutable business concepts.

They:

- have no identity;
- are immutable whenever practical;
- exist only as part of an Entity or Composed Domain Object.

Current Value Objects:

- SessionId
- PlayerId
- GameInput
- VoteResult
- SessionConfiguration
- SaveMetadata
- PlayerStatistics

---

## 3.3 Composed Domain Objects

Composed Domain Objects are mutable objects owned exclusively by an Aggregate Root.

They:

- have no identity;
- are never persisted independently;
- never exist outside the Aggregate;
- encapsulate state and behaviour.

Current Composed Domain Objects:

- InputQueue
- Metrics
- VoteRound
- PlayerManager
- SaveManager
- SessionStateMachine

---

# 4. Aggregate Root

The system contains a single Aggregate Root.

```text
GameSession
```

Every business operation starts through this entity.

No external component may directly modify internal domain objects.

All state mutations occur through GameSession public methods.

---

# 5. Domain UML

```text
+---------------------------------------------------------------+
|                        GameSession                            |
+---------------------------------------------------------------+
| - sessionId : SessionId                                       |
| - configuration : SessionConfiguration                        |
| - players : PlayerManager                                     |
| - inputQueue : InputQueue                                     |
| - metrics : Metrics                                           |
| - saveManager : SaveManager                                   |
| - stateMachine : SessionStateMachine                          |
| - currentVote : VoteRound?                                    |
+---------------------------------------------------------------+
| + start()                                                     |
| + stop()                                                      |
| + pause()                                                     |
| + resume()                                                    |
| + submitInput(GameInput)                                      |
| + connectPlayer(Player)                                       |
| + disconnectPlayer(PlayerId)                                  |
| + changeControlMode(ControlMode)                              |
| + createSnapshot()                                            |
| + restoreSnapshot()                                           |
+---------------------------------------------------------------+

                 ◆ owns

    +-----------+-----------+-----------+-----------+

    ▼           ▼           ▼           ▼

PlayerManager  InputQueue  Metrics  SaveManager

        │

        ▼

    Player (Entity)

        │

        ▼

PlayerStatistics
```

---

# 6. Entities

---

## 6.1 GameSession

### Responsibility

Represents one running game session.

Acts as the Aggregate Root of the Domain.

### Responsibilities

- Protect business invariants
- Coordinate player lifecycle
- Receive player inputs
- Manage control mode
- Coordinate save operations
- Coordinate voting
- Expose session state

### Owns

- PlayerManager
- InputQueue
- Metrics
- SaveManager
- SessionStateMachine
- Current Vote

No internal object may be modified directly from outside the Aggregate.

---

## 6.2 Player

### Responsibility

Represents one participant of the session.

### Attributes

```text
PlayerId

DisplayName

PlayerStatistics
```

A Player represents only business identity.

It has no knowledge of transport protocols or infrastructure.

---

# 7. Value Objects

---

## SessionId

Unique session identifier.

Immutable.

---

## PlayerId

Unique player identifier.

Immutable.

---

## GameInput

Represents one player action.

Attributes:

```text
Button

Timestamp

PlayerId
```

Immutable.

---

## VoteResult

Represents the result of one completed voting round.

Immutable.

---

## SessionConfiguration

Contains all runtime configuration.

Examples:

- Control mode
- Voting interval
- Autosave interval

Immutable during runtime unless explicitly replaced.

---

## SaveMetadata

Contains metadata describing the latest save state.

Examples:

- Last save timestamp
- Save count

Immutable.

---

## PlayerStatistics

Contains statistics describing one player.

Examples:

- Submitted commands
- Winning votes
- Connected duration

Immutable snapshots of player activity.

---

# 8. Composed Domain Objects

---

## InputQueue

Maintains the ordered collection of pending player inputs.

Responsibilities:

- enqueue
- dequeue
- peek
- clear
- size

The queue is agnostic of the current Control Mode.

FIFO and Voting only differ in how queued inputs are consumed.

---

## Metrics

Maintains live session statistics.

Examples:

- Total commands
- Connected players
- Votes processed
- Frames executed

Metrics expose behaviour required to update statistics while encapsulating their internal state.

---

## VoteRound

Represents one active voting window.

Responsibilities:

- collect votes
- close voting
- expose collected votes

A VoteRound exists only while a voting window is active.

---

## PlayerManager

Responsible for managing all connected players.

Responsibilities:

- connect player
- disconnect player
- search player
- enumerate players
- count players

Owns every Player entity.

---

## SaveManager

Coordinates save-related domain operations.

Responsibilities:

- create snapshot
- restore snapshot
- update save metadata

Infrastructure persistence remains outside the Domain.

---

## SessionStateMachine

Responsible for validating session state transitions.

Supported states:

```text
STARTING

RUNNING

PAUSED

STOPPING

STOPPED
```

Illegal transitions are rejected through Domain Exceptions.

---

# 9. Enumerations

---

## Button

```text
UP
DOWN
LEFT
RIGHT
A
B
START
SELECT
```

---

## ControlMode

```text
FIFO

VOTING
```

---

## SessionState

```text
STARTING

RUNNING

PAUSED

STOPPING

STOPPED
```

---

## PlayerState

```text
CONNECTED

DISCONNECTED
```

---

# 10. Domain Services

Domain Services encapsulate business logic that does not naturally belong to a single Entity or Composed Domain Object.

---

## FIFOResolver

Determines the next command using FIFO ordering.

Input:

```text
InputQueue
```

Output:

```text
GameInput
```

Stateless.

---

## VoteResolver

Determines the winning command of a completed VoteRound.

Input:

```text
VoteRound
```

Output:

```text
VoteResult
```

Stateless.

---

## MetricsCalculator

Calculates derived statistics.

Examples:

- Commands per minute
- Average vote duration
- Active player ratio

Stateless.

---

## SessionValidator

Validates business constraints that span multiple domain objects.

Examples:

- Session lifecycle
- Configuration consistency
- Aggregate invariants

Stateless.

---

# 11. Domain Exceptions

The Domain defines business-specific exceptions.

Examples:

```text
SessionNotRunningException

PlayerAlreadyConnectedException

PlayerNotConnectedException

InvalidControlModeException

InvalidSessionStateException

VoteAlreadyRunningException
```

Exceptions remain completely independent from transport protocols.

---

# 12. Internal Relationships

```text
GameSession

◆── PlayerManager

│     ◆── Player (1..*)

│             ◆── PlayerStatistics

│

◆── InputQueue

◆── Metrics

◆── SaveManager

◆── SessionStateMachine

◆── VoteRound (0..1)

◆── SessionConfiguration

◆── SaveMetadata
```

All objects belong exclusively to the GameSession aggregate.

---

# 13. Domain Dependency DAG

```text
Enums

↓

Value Objects

↓

Composed Domain Objects

↓

Entities

↓

Domain Services

↓

Exceptions
```

The Domain layer shall not contain cyclic dependencies.

---

# 14. Implementation Rules

- The Aggregate Root protects every business invariant.
- Entities expose business behaviour rather than mutable state.
- Value Objects remain immutable whenever practical.
- Composed Domain Objects encapsulate mutable state owned by the Aggregate.
- Domain Services remain stateless.
- Constructors must always create valid objects.
- No infrastructure imports are permitted.
- Every public method shall represent a business operation.
- Circular dependencies are forbidden.
