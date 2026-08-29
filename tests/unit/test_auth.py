"""
blender-mcp-ultra — Authentication Tests
Tests for token-based authentication.
"""

import os
import sys
import time

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


class TestAuthenticator:
    """Tests for Authenticator."""

    def test_authenticator_import(self):
        from mcp_ultra.infrastructure.security.auth import Authenticator

        assert Authenticator is not None

    def test_generate_token(self):
        from mcp_ultra.infrastructure.security.auth import Authenticator

        auth = Authenticator()
        token = auth.generate_token("user1")
        assert token is not None
        assert len(token) == 64  # hex token

    def test_validate_token(self):
        from mcp_ultra.infrastructure.security.auth import Authenticator

        auth = Authenticator()
        token = auth.generate_token("user1")
        auth_token = auth.validate_token(token)
        assert auth_token is not None
        assert auth_token.user_id == "user1"

    def test_validate_invalid_token(self):
        from mcp_ultra.infrastructure.security.auth import Authenticator

        auth = Authenticator()
        auth_token = auth.validate_token("invalid_token")
        assert auth_token is None

    def test_token_expiration(self):
        from mcp_ultra.infrastructure.security.auth import Authenticator

        auth = Authenticator()
        token = auth.generate_token("user1", expires_in=1)  # 1 second
        time.sleep(2)
        auth_token = auth.validate_token(token)
        assert auth_token is None

    def test_check_permission(self):
        from mcp_ultra.infrastructure.security.auth import Authenticator

        auth = Authenticator()
        token = auth.generate_token("user1", permissions=["read", "write"])
        assert auth.check_permission(token, "read") is True
        assert auth.check_permission(token, "write") is True
        assert auth.check_permission(token, "admin") is False

    def test_revoke_token(self):
        from mcp_ultra.infrastructure.security.auth import Authenticator

        auth = Authenticator()
        token = auth.generate_token("user1")
        assert auth.revoke_token(token) is True
        assert auth.validate_token(token) is None

    def test_revoke_all_user_tokens(self):
        from mcp_ultra.infrastructure.security.auth import Authenticator

        auth = Authenticator()
        token1 = auth.generate_token("user1")
        token2 = auth.generate_token("user1")
        count = auth.revoke_all_user_tokens("user1")
        assert count == 2
        assert auth.validate_token(token1) is None
        assert auth.validate_token(token2) is None

    def test_get_user_tokens(self):
        from mcp_ultra.infrastructure.security.auth import Authenticator

        auth = Authenticator()
        auth.generate_token("user1")
        auth.generate_token("user1")
        tokens = auth.get_user_tokens("user1")
        assert len(tokens) == 2


class TestAuthSingleton:
    """Tests for auth singleton."""

    def test_singleton(self):
        from mcp_ultra.infrastructure.security.auth import get_authenticator

        auth1 = get_authenticator()
        auth2 = get_authenticator()
        assert auth1 is auth2


class TestAuthConvenience:
    """Tests for convenience functions."""

    def test_generate_token_convenience(self):
        from mcp_ultra.infrastructure.security.auth import generate_token

        token = generate_token("user1")
        assert token is not None

    def test_validate_token_convenience(self):
        from mcp_ultra.infrastructure.security.auth import generate_token, validate_token

        token = generate_token("user1")
        auth_token = validate_token(token)
        assert auth_token is not None

    def test_check_permission_convenience(self):
        from mcp_ultra.infrastructure.security.auth import check_permission, generate_token

        token = generate_token("user1", permissions=["read"])
        assert check_permission(token, "read") is True
        assert check_permission(token, "write") is False


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
