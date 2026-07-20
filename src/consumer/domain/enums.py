from enum import Enum, auto


class Button(Enum):
    UP = auto()
    DOWN = auto()
    LEFT = auto()
    RIGHT = auto()
    A = auto()
    B = auto()
    START = auto()
    SELECT = auto()


class ControlMode(Enum):
    FIFO = auto()
    VOTING = auto()


class SessionState(Enum):
    STARTING = auto()
    RUNNING = auto()
    PAUSED = auto()
    STOPPING = auto()
    STOPPED = auto()


class PlayerState(Enum):
    CONNECTED = auto()
    DISCONNECTED = auto()
