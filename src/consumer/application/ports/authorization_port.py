from __future__ import annotations

from abc import ABC, abstractmethod


class AuthorizationPort(ABC):
    @abstractmethod
    def is_admin(self, user_id: int) -> bool: ...
