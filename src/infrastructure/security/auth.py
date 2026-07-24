"""
blender-mcp-ultra — Authentication Module
Token-based authentication for MCP server.
"""
import os
import secrets
import hashlib
import time
from typing import Optional, Dict, Any
from dataclasses import dataclass


@dataclass
class AuthToken:
    """Authentication token."""
    token: str
    user_id: str
    created_at: float
    expires_at: float
    permissions: list


class Authenticator:
    """
    Token-based authentication system.
    
    Features:
    - Token generation
    - Token validation
    - Permission management
    - Token expiration
    """
    
    def __init__(self, secret_key: str = None):
        """
        Initialize authenticator.
        
        Args:
            secret_key: Secret key for token generation
        """
        self.secret_key = secret_key or os.environ.get("MCP_SECRET_KEY", secrets.token_hex(32))
        self._tokens: Dict[str, AuthToken] = {}
        self._user_permissions: Dict[str, list] = {}
    
    def generate_token(self, user_id: str, permissions: list = None, expires_in: int = 86400) -> str:
        """
        Generate a new authentication token.
        
        Args:
            user_id: User identifier
            permissions: List of permissions
            expires_in: Expiration time in seconds (default: 24 hours)
            
        Returns:
            Token string
        """
        token = secrets.token_hex(32)
        expires_at = time.time() + expires_in
        
        auth_token = AuthToken(
            token=token,
            user_id=user_id,
            created_at=time.time(),
            expires_at=expires_at,
            permissions=permissions or ["read", "write"]
        )
        
        self._tokens[token] = auth_token
        self._user_permissions[user_id] = permissions or ["read", "write"]
        
        return token
    
    def validate_token(self, token: str) -> Optional[AuthToken]:
        """
        Validate an authentication token.
        
        Args:
            token: Token to validate
            
        Returns:
            AuthToken if valid, None otherwise
        """
        auth_token = self._tokens.get(token)
        if auth_token is None:
            return None
        
        # Check expiration
        if time.time() > auth_token.expires_at:
            del self._tokens[token]
            return None
        
        return auth_token
    
    def check_permission(self, token: str, permission: str) -> bool:
        """
        Check if token has a specific permission.
        
        Args:
            token: Authentication token
            permission: Permission to check
            
        Returns:
            True if permission granted
        """
        auth_token = self.validate_token(token)
        if auth_token is None:
            return False
        
        return permission in auth_token.permissions
    
    def revoke_token(self, token: str) -> bool:
        """
        Revoke an authentication token.
        
        Args:
            token: Token to revoke
            
        Returns:
            True if revoked
        """
        if token in self._tokens:
            del self._tokens[token]
            return True
        return False
    
    def revoke_all_user_tokens(self, user_id: str) -> int:
        """
        Revoke all tokens for a user.
        
        Args:
            user_id: User identifier
            
        Returns:
            Number of tokens revoked
        """
        count = 0
        tokens_to_remove = []
        
        for token, auth_token in self._tokens.items():
            if auth_token.user_id == user_id:
                tokens_to_remove.append(token)
        
        for token in tokens_to_remove:
            del self._tokens[token]
            count += 1
        
        return count
    
    def get_user_tokens(self, user_id: str) -> list:
        """
        Get all tokens for a user.
        
        Args:
            user_id: User identifier
            
        Returns:
            List of AuthToken objects
        """
        return [
            token for token in self._tokens.values()
            if token.user_id == user_id
        ]


# Singleton instance
_authenticator = None

def get_authenticator(**kwargs) -> Authenticator:
    """Get singleton authenticator instance."""
    global _authenticator
    if _authenticator is None:
        _authenticator = Authenticator(**kwargs)
    return _authenticator


def generate_token(user_id: str, permissions: list = None) -> str:
    """Convenience function to generate token."""
    return get_authenticator().generate_token(user_id, permissions)


def validate_token(token: str) -> Optional[AuthToken]:
    """Convenience function to validate token."""
    return get_authenticator().validate_token(token)


def check_permission(token: str, permission: str) -> bool:
    """Convenience function to check permission."""
    return get_authenticator().check_permission(token, permission)
