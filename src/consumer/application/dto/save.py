from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class AutosaveRequest:
    pass


@dataclass(frozen=True)
class AutosaveResponse:
    last_save_at: datetime
    save_count: int


@dataclass(frozen=True)
class ManualSaveRequest:
    pass


@dataclass(frozen=True)
class ManualSaveResponse:
    last_save_at: datetime
    save_count: int
