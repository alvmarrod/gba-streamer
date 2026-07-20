from __future__ import annotations

import os
from unittest.mock import patch

from consumer.infrastructure.authorization.env_admin_authorizer import (
    EnvAdminAuthorizer,
)


class TestEnvAdminAuthorizer:
    def test_is_admin_for_listed_user(self) -> None:
        with patch.dict(os.environ, {"ADMIN_USER_IDS": "123,456"}, clear=True):
            auth = EnvAdminAuthorizer()
            assert auth.is_admin(123) is True
            assert auth.is_admin(456) is True

    def test_is_not_admin_for_unlisted_user(self) -> None:
        with patch.dict(os.environ, {"ADMIN_USER_IDS": "123"}, clear=True):
            auth = EnvAdminAuthorizer()
            assert auth.is_admin(999) is False

    def test_empty_env_yields_no_admins(self) -> None:
        with patch.dict(os.environ, {}, clear=True):
            auth = EnvAdminAuthorizer()
            assert auth.is_admin(123) is False

    def test_empty_string_yields_no_admins(self) -> None:
        with patch.dict(os.environ, {"ADMIN_USER_IDS": ""}, clear=True):
            auth = EnvAdminAuthorizer()
            assert auth.is_admin(123) is False

    def test_handles_spaces_around_ids(self) -> None:
        with patch.dict(os.environ, {"ADMIN_USER_IDS": " 123 , 456 "}, clear=True):
            auth = EnvAdminAuthorizer()
            assert auth.is_admin(123) is True
            assert auth.is_admin(456) is True
