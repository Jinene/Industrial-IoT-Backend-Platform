import logging
import secrets
from datetime import datetime, timedelta, timezone
from typing import Any, Optional

from fastapi import Depends, HTTPException, Security, status
from fastapi.security import APIKeyHeader

from app.core.config import settings

logger = logging.getLogger(__name__)

# Simple API key scheme (pragmatic for internal/industrial services)
# You can later replace with OAuth2/JWT if needed.
API_KEY_HEADER_NAME = "X-API-Key"
api_key_header = APIKeyHeader(name=API_KEY_HEADER_NAME, auto_error=False)


def _get_configured_api_key() -> Optional[str]:
    """
    Fetch API key from env. If not configured, authentication can be disabled.
    """
    # Optional env var; if missing, auth is "off" unless you enforce it.
    return getattr(settings, "api_key", None)


def generate_api_key(length: int = 32) -> str:
    """
    Generate a cryptographically secure API key for clients.
    """
    # token_urlsafe produces variable length; for predictable size use token_hex
    # 32 bytes -> 64 hex chars
    if length <= 0:
        length = 32
    return secrets.token_hex(length)


def require_api_key(api_key: Optional[str] = Security(api_key_header)) -> str:
    """
    Dependency that enforces API key if configured.
    If API key is not configured in env, it allows requests (dev-friendly).
    """
    configured = _get_configured_api_key()
    if not configured:
        # Auth disabled (dev mode). You can flip this to enforce by default if you prefer.
        return ""

    if not api_key or api_key != configured:
        logger.warning("Unauthorized request: invalid API key")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API key",
        )

    return api_key


# ---- Optional: Signed "service tokens" (lightweight, no external libs) ----
# This is NOT a full JWT implementation; it's a pragmatic signed token that can be useful
# for internal service-to-service calls. If you want real JWT, tell me and I’ll add it.

def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def create_signed_token(subject: str, secret: str, expires_in_seconds: int = 3600) -> str:
    """
    Create a simple signed token: subject|exp_epoch|signature
    signature = hex(hmac_sha256(subject|exp, secret))
    """
    import hmac
    import hashlib

    exp = int((_utcnow() + timedelta(seconds=expires_in_seconds)).timestamp())
    message = f"{subject}|{exp}".encode("utf-8")
    sig = hmac.new(secret.encode("utf-8"), message, hashlib.sha256).hexdigest()
    return f"{subject}|{exp}|{sig}"


def verify_signed_token(token: str, secret: str) -> dict[str, Any]:
    """
    Verify token created by create_signed_token.
    Returns {"subject": ..., "exp": ...} if valid; raises HTTPException otherwise.
    """
    import hmac
    import hashlib

    parts = token.split("|")
    if len(parts) != 3:
        raise HTTPException(status_code=401, detail="Invalid token format")

    subject, exp_str, sig = parts
    try:
        exp = int(exp_str)
    except ValueError:
        raise HTTPException(status_code=401, detail="Invalid token expiry")

    if int(_utcnow().timestamp()) > exp:
        raise HTTPException(status_code=401, detail="Token expired")

    message = f"{subject}|{exp}".encode("utf-8")
    expected = hmac.new(secret.encode("utf-8"), message, hashlib.sha256).hexdigest()

    if not hmac.compare_digest(expected, sig):
        raise HTTPException(status_code=401, detail="Invalid token signature")

    return {"subject": subject, "exp": exp}

