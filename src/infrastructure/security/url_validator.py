"""
blender-mcp-ultra — URL Validator
Validates URLs against a whitelist of allowed domains.
Prevents SSRF and other URL-based attacks.
"""
import re
from typing import Set, List, Optional
from urllib.parse import urlparse
from dataclasses import dataclass


class URLError(Exception):
    """Raised when URL violates security policies."""
    pass


@dataclass
class URLValidationResult:
    """Result of URL validation."""
    is_safe: bool
    errors: List[str]
    warnings: List[str]


class URLValidator:
    """Validates URLs against security policies."""
    
    # Default allowed domains
    DEFAULT_ALLOWED_DOMAINS: Set[str] = {
        # Asset providers
        'polyhaven.com',
        'sketchfab.com',
        'ambientcg.com',
        
        # AI providers
        'api.openai.com',
        'api.anthropic.com',
        'api.deepseek.com',
        'generativelanguage.googleapis.com',
        'openrouter.ai',
        
        # Local
        'localhost',
        '127.0.0.1',
    }
    
    # Blocked patterns
    BLOCKED_PATTERNS: List[str] = [
        r'file://',           # Local file access
        r'ftp://',            # FTP
        r'data:',             # Data URLs (can contain code)
        r'javascript:',       # JavaScript URLs
        r'vbscript:',         # VBScript URLs
    ]
    
    def __init__(self, custom_allowed: Optional[Set[str]] = None):
        """
        Initialize URL validator.
        
        Args:
            custom_allowed: Additional allowed domains
        """
        self.allowed_domains = self.DEFAULT_ALLOWED_DOMAINS.copy()
        if custom_allowed:
            self.allowed_domains.update(custom_allowed)
        
        self.blocked_patterns = [re.compile(p, re.IGNORECASE) 
                                 for p in self.BLOCKED_PATTERNS]
    
    def validate(self, url: str) -> URLValidationResult:
        """
        Validate a URL.
        
        Args:
            url: URL to validate
            
        Returns:
            URLValidationResult with is_safe, errors, warnings
        """
        errors = []
        warnings = []
        
        # Check blocked patterns
        for pattern in self.blocked_patterns:
            if pattern.search(url):
                errors.append(f"URL matches blocked pattern: {pattern.pattern}")
        
        # Parse URL
        try:
            parsed = urlparse(url)
        except Exception as e:
            errors.append(f"Invalid URL format: {e}")
            return URLValidationResult(
                is_safe=False,
                errors=errors,
                warnings=warnings
            )
        
        # Check scheme
        if parsed.scheme not in ('http', 'https', ''):
            errors.append(f"Invalid scheme: {parsed.scheme}")
        
        # Check domain
        domain = parsed.hostname or ''
        if domain and domain not in self.allowed_domains:
            # Check if it's a subdomain of allowed domain
            is_subdomain = any(
                domain.endswith(f'.{allowed}') or domain == allowed
                for allowed in self.allowed_domains
            )
            if not is_subdomain:
                errors.append(f"Domain not allowed: {domain}")
        
        # Check for IP addresses (potential SSRF)
        if self._is_ip_address(domain):
            warnings.append(f"IP address detected: {domain}")
            if domain not in ('localhost', '127.0.0.1', '0.0.0.0'):
                errors.append(f"External IP address not allowed: {domain}")
        
        is_safe = len(errors) == 0
        
        return URLValidationResult(
            is_safe=is_safe,
            errors=errors,
            warnings=warnings
        )
    
    def validate_strict(self, url: str) -> None:
        """
        Validate URL strictly - raises exception if not safe.
        
        Args:
            url: URL to validate
            
        Raises:
            URLError: If URL validation fails
        """
        result = self.validate(url)
        if not result.is_safe:
            raise URLError(
                f"URL validation failed: {'; '.join(result.errors)}"
            )
    
    def _is_ip_address(self, host: str) -> bool:
        """Check if host is an IP address."""
        if not host:
            return False
        # IPv4
        if re.match(r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$', host):
            return True
        # IPv6 (simplified check)
        if ':' in host:
            return True
        return False
    
    def add_allowed(self, domains: Set[str]) -> None:
        """Add domains to allowed list."""
        self.allowed_domains.update(domains)
    
    def remove_allowed(self, domains: Set[str]) -> None:
        """Remove domains from allowed list."""
        self.allowed_domains -= domains
    
    def get_allowed_domains(self) -> Set[str]:
        """Get current allowed domains."""
        return self.allowed_domains.copy()


# Singleton instance
_validator = None

def get_validator(**kwargs) -> URLValidator:
    """Get singleton validator instance."""
    global _validator
    if _validator is None:
        _validator = URLValidator(**kwargs)
    return _validator

def validate_url(url: str) -> URLValidationResult:
    """Convenience function to validate URL."""
    return get_validator().validate(url)

def validate_url_strict(url: str) -> None:
    """Convenience function to validate URL strictly."""
    get_validator().validate_strict(url)
