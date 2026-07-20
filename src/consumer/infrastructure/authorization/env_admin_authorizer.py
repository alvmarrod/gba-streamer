from __future__ import annotations

import os

from consumer.application.ports.authorization_port import AuthorizationPort


class EnvAdminAuthorizer(AuthorizationPort):
    def __init__(self) -> None:
        raw = os.environ.get("ADMIN_USER_IDS", "")
        self._admin_ids: set[int] = {
            int(uid.strip()) for uid in raw.split(",") if uid.strip()
        }

    def is_admin(self, user_id: int) -> bool:
        return user_id in self._admin_ids
