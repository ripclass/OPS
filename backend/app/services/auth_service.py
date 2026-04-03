"""
Supabase-backed API authentication helpers.
"""

from __future__ import annotations

import threading
import time
from typing import Any, Dict, Optional

from supabase import create_client

from ..config import Config


class AuthConfigurationError(RuntimeError):
    """Raised when auth is enabled but required config is missing."""


class AuthError(RuntimeError):
    """Raised when a bearer token is missing or invalid."""


_auth_client = None
_cache_lock = threading.Lock()
_token_cache: Dict[str, Dict[str, Any]] = {}
_CACHE_TTL_SECONDS = 300


def _get_auth_client():
    global _auth_client
    if not Config.SUPABASE_URL or not Config.SUPABASE_SERVICE_ROLE_KEY:
        raise AuthConfigurationError(
            "SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY must be configured when AUTH_REQUIRED is enabled"
        )

    if _auth_client is None:
        _auth_client = create_client(
            Config.SUPABASE_URL,
            Config.SUPABASE_SERVICE_ROLE_KEY,
        )
    return _auth_client


def _read_cached_user(token: str) -> Optional[Dict[str, Any]]:
    with _cache_lock:
        cached = _token_cache.get(token)
        if not cached:
            return None
        if cached["expires_at"] <= time.time():
            _token_cache.pop(token, None)
            return None
        return cached["user"]


def _store_cached_user(token: str, user: Dict[str, Any]) -> None:
    with _cache_lock:
        _token_cache[token] = {
            "user": user,
            "expires_at": time.time() + _CACHE_TTL_SECONDS,
        }


def verify_access_token(token: str) -> Dict[str, Any]:
    """Validate a Supabase access token and return the authenticated user payload."""
    token = (token or "").strip()
    if not token:
        raise AuthError("Missing access token")

    cached_user = _read_cached_user(token)
    if cached_user is not None:
        return cached_user

    client = _get_auth_client()
    response = client.auth.get_user(token)
    user = getattr(response, "user", None)
    if user is None:
        raise AuthError("Invalid or expired access token")

    user_dict = user.model_dump() if hasattr(user, "model_dump") else dict(user)
    _store_cached_user(token, user_dict)
    return user_dict
