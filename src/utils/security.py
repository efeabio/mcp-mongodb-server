"""
Security utilities for the FastMCP MongoDB Server.

This module provides functions for sanitizing sensitive information
and secure handling of credentials.
"""

import re
from typing import Any, Dict, Union
from urllib.parse import urlparse, urlunparse


def sanitize_uri(uri: str) -> str:
    """
    Sanitize MongoDB URI by masking credentials.
    
    Args:
        uri: MongoDB connection URI
        
    Returns:
        Sanitized URI with masked credentials
        
    Examples:
        >>> sanitize_uri("mongodb://user:pass@localhost:27017/db")
        "mongodb://user:***@localhost:27017/db"
        >>> sanitize_uri("mongodb://localhost:27017")
        "mongodb://localhost:27017"
    """
    try:
        parsed = urlparse(uri)
        if parsed.password:
            # Replace password with ***
            netloc = parsed.netloc.replace(f":{parsed.password}@", ":***@")
            sanitized = parsed._replace(netloc=netloc)
            return urlunparse(sanitized)
        return uri
    except Exception:
        # If parsing fails, try regex replacement as fallback
        return re.sub(r'://([^:]+):([^@]+)@', r'://\1:***@', uri)


def sanitize_log_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Sanitize log data by removing or masking sensitive information.
    
    Args:
        data: Dictionary containing log data
        
    Returns:
        Sanitized dictionary with sensitive data masked
    """
    if not isinstance(data, dict):
        return data
    
    sanitized = {}
    sensitive_keys = {
        'password', 'passwd', 'pwd', 'secret', 'token', 'key', 'auth',
        'credential', 'credentials', 'api_key', 'apikey', 'access_key',
        'private_key', 'mongodb_password'
    }
    
    for key, value in data.items():
        key_lower = key.lower()
        
        if any(sensitive in key_lower for sensitive in sensitive_keys):
            if value:
                sanitized[key] = "***" if isinstance(value, str) else "[MASKED]"
            else:
                sanitized[key] = value
        elif key_lower == 'uri' and isinstance(value, str):
            sanitized[key] = sanitize_uri(value)
        elif isinstance(value, dict):
            sanitized[key] = sanitize_log_data(value)
        elif isinstance(value, (list, tuple)):
            sanitized[key] = [
                sanitize_log_data(item) if isinstance(item, dict) else item
                for item in value
            ]
        else:
            sanitized[key] = value
    
    return sanitized


def mask_string(value: str, show_chars: int = 3) -> str:
    """
    Mask a string showing only the first few characters.
    
    Args:
        value: String to mask
        show_chars: Number of characters to show at the beginning
        
    Returns:
        Masked string
        
    Examples:
        >>> mask_string("password123", 3)
        "pas***"
        >>> mask_string("ab", 3)
        "***"
    """
    if not value or not isinstance(value, str):
        return "***"
    
    if len(value) <= show_chars:
        return "***"
    
    return value[:show_chars] + "***"


def sanitize_connection_params(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Sanitize connection parameters for logging.
    
    Args:
        params: Connection parameters dictionary
        
    Returns:
        Sanitized parameters dictionary
    """
    sanitized = params.copy()
    
    if 'password' in sanitized and sanitized['password']:
        sanitized['password'] = mask_string(str(sanitized['password']))
    
    if 'username' in sanitized and sanitized['username']:
        # Don't fully mask username, just show first few chars
        username = str(sanitized['username'])
        if len(username) > 3:
            sanitized['username'] = username[:2] + "***"
    
    # Sanitize any URI that might contain credentials
    for key in ['uri', 'connection_string', 'mongodb_uri']:
        if key in sanitized and sanitized[key]:
            sanitized[key] = sanitize_uri(str(sanitized[key]))
    
    return sanitized


def is_sensitive_field(field_name: str) -> bool:
    """
    Check if a field name indicates sensitive information.
    
    Args:
        field_name: Field name to check
        
    Returns:
        True if the field is considered sensitive
    """
    sensitive_patterns = [
        'password', 'passwd', 'pwd', 'secret', 'token', 'key',
        'auth', 'credential', 'api', 'private', 'access'
    ]
    
    field_lower = field_name.lower()
    return any(pattern in field_lower for pattern in sensitive_patterns)


class SecureLoggerAdapter:
    """
    Logger adapter that automatically sanitizes sensitive information.
    """
    
    def __init__(self, logger):
        self.logger = logger
    
    def info(self, message: str, **kwargs):
        """Log info message with sanitized data."""
        sanitized_kwargs = sanitize_log_data(kwargs)
        return self.logger.info(message, **sanitized_kwargs)
    
    def error(self, message: str, **kwargs):
        """Log error message with sanitized data."""
        sanitized_kwargs = sanitize_log_data(kwargs)
        return self.logger.error(message, **sanitized_kwargs)
    
    def warning(self, message: str, **kwargs):
        """Log warning message with sanitized data."""
        sanitized_kwargs = sanitize_log_data(kwargs)
        return self.logger.warning(message, **sanitized_kwargs)
    
    def debug(self, message: str, **kwargs):
        """Log debug message with sanitized data."""
        sanitized_kwargs = sanitize_log_data(kwargs)
        return self.logger.debug(message, **sanitized_kwargs)