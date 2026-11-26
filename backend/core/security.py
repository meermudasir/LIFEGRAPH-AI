"""
LifeGraph AI - Core Security & Session Management Module
Handles:
- Secure password hashing and verification using bcrypt (with pbkdf2 fallback)
- JWT token minting, signing, and cryptographic decoding
- Secure HttpOnly, Secure, SameSite cookie management
- Session isolation helpers
"""

import os
import time
import hmac
import json
import base64
import hashlib
import secrets
import urllib.parse
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any, Tuple
from fastapi import Request, Response

from backend.config import settings

# Canonical JWT Issuer Identifier
JWT_ISSUER: str = "lifegraph-ai"

# ------------------------------------------------------------------------------
# 1. BCRYPT PASSWORD HASHING & VERIFICATION
# ------------------------------------------------------------------------------

try:
    import bcrypt
    _HAS_BCRYPT = True
except ImportError:
    _HAS_BCRYPT = False


# OWASP Recommended Iteration Count for PBKDF2-HMAC-SHA256
PBKDF2_RECOMMENDED_ITERATIONS: int = 600_000


def hash_password(password: str) -> str:
    """
    Hashes a plain-text password using bcrypt with a random salt.
    Falls back to PBKDF2-HMAC-SHA256 if bcrypt library is not yet installed.

    Security Parameters:
    - Primary: bcrypt with cost factor rounds=12 (adaptive, resistant to GPU attacks).
    - Fallback: PBKDF2-HMAC-SHA256 with 600,000 iterations (OWASP Password Storage guidance),
      salted with 16 cryptographically secure random bytes (32 hex characters).
    - Verification Compatibility: Existing hashes stored with previous iteration counts
      (e.g., $pbkdf2$100000$...) parse their iteration count dynamically from the hash prefix
      and continue to verify seamlessly without format changes or silent breakage.
    - Downgrade Protection: Bcrypt hashes are NEVER matched against PBKDF2; if bcrypt is missing,
      verification of bcrypt hashes fails closed rather than downgrading.
    """
    if not password:
        raise ValueError("Password cannot be empty.")

    password_bytes = password.encode("utf-8")

    if _HAS_BCRYPT:
        salt = bcrypt.gensalt(rounds=12)
        hashed = bcrypt.hashpw(password_bytes, salt)
        return hashed.decode("utf-8")
    else:
        # Fallback to PBKDF2-HMAC-SHA256 (600,000 rounds, 16-byte random salt)
        salt = secrets.token_hex(16)
        key = hashlib.pbkdf2_hmac("sha256", password_bytes, salt.encode("utf-8"), PBKDF2_RECOMMENDED_ITERATIONS)
        return f"$pbkdf2${PBKDF2_RECOMMENDED_ITERATIONS}${salt}${key.hex()}"


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifies a plain-text password against a stored hash.
    Safely handles both bcrypt ($2a$, $2b$, $2y$) and PBKDF2 format.
    """
    if not plain_password or not hashed_password:
        return False

    try:
        if hashed_password.startswith(("$2a$", "$2b$", "$2y$")):
            if _HAS_BCRYPT:
                return bcrypt.checkpw(
                    plain_password.encode("utf-8"),
                    hashed_password.encode("utf-8"),
                )
            else:
                return False

        if hashed_password.startswith("$pbkdf2$"):
            parts = hashed_password.split("$")
            if len(parts) != 5:
                return False
            iterations = int(parts[2])
            salt = parts[3]
            expected_hash = parts[4]
            test_key = hashlib.pbkdf2_hmac(
                "sha256", plain_password.encode("utf-8"), salt.encode("utf-8"), iterations
            )
            return hmac.compare_digest(test_key.hex(), expected_hash)

        return False
    except Exception:
        return False


# ------------------------------------------------------------------------------
# 2. JWT TOKEN GENERATION & VERIFICATION
# ------------------------------------------------------------------------------

try:
    import jwt
    _HAS_PYJWT = True
except ImportError:
    _HAS_PYJWT = False


def create_access_token(
    data: Dict[str, Any],
    expires_delta: Optional[timedelta] = None,
) -> str:
    """
    Generates a cryptographically signed JWT access token.
    Default lifetime is configured in settings.ACCESS_TOKEN_EXPIRE_MINUTES.
    """
    to_encode = data.copy()
    now = datetime.now(timezone.utc)

    if expires_delta:
        expire = now + expires_delta
    else:
        expire = now + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({
        "exp": int(expire.timestamp()),
        "iat": int(now.timestamp()),
        "iss": JWT_ISSUER,
    })

    if _HAS_PYJWT:
        return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    else:
        # Standard HMAC-SHA256 JWT implementation fallback
        header = {"alg": "HS256", "typ": "JWT"}
        header_b64 = base64.urlsafe_b64encode(json.dumps(header).encode()).decode().rstrip("=")
        payload_b64 = base64.urlsafe_b64encode(json.dumps(to_encode).encode()).decode().rstrip("=")
        signing_input = f"{header_b64}.{payload_b64}"
        signature = hmac.new(
            settings.SECRET_KEY.encode(),
            signing_input.encode(),
            hashlib.sha256,
        ).digest()
        sig_b64 = base64.urlsafe_b64encode(signature).decode().rstrip("=")
        return f"{signing_input}.{sig_b64}"


def decode_access_token(token: str) -> Optional[Dict[str, Any]]:
    """
    Decodes and validates a JWT access token signature, issuer, and expiration.
    Returns the token payload dictionary, or None if invalid or expired.
    """
    if not token or not isinstance(token, str):
        return None

    try:
        if _HAS_PYJWT:
            payload = jwt.decode(
                token,
                settings.SECRET_KEY,
                algorithms=[settings.ALGORITHM],
                issuer=JWT_ISSUER,
                options={"verify_exp": True, "verify_iss": True},
            )
        else:
            # Fallback HMAC-SHA256 verification
            parts = token.split(".")
            if len(parts) != 3:
                return None
            header_b64, payload_b64, sig_b64 = parts
            signing_input = f"{header_b64}.{payload_b64}"
            expected_sig = hmac.new(
                settings.SECRET_KEY.encode(),
                signing_input.encode(),
                hashlib.sha256,
            ).digest()
            # Restore padding
            sig_padded = sig_b64 + "=" * (-len(sig_b64) % 4)
            actual_sig = base64.urlsafe_b64decode(sig_padded.encode())

            if not hmac.compare_digest(expected_sig, actual_sig):
                return None

            payload_padded = payload_b64 + "=" * (-len(payload_b64) % 4)
            payload_json = base64.urlsafe_b64decode(payload_padded.encode()).decode()
            payload = json.loads(payload_json)

            # Enforce issuer verification
            if payload.get("iss") != JWT_ISSUER:
                return None

            # Check expiration
            exp = payload.get("exp")
            if exp and datetime.now(timezone.utc).timestamp() > exp:
                return None

        # Verify that the JWT subject (sub) is present and non-empty before accepting a token
        sub = payload.get("sub")
        if not sub or not isinstance(sub, str) or not sub.strip():
            return None

        return payload
    except Exception:
        return None


# ------------------------------------------------------------------------------
# 3. SECURE HTTPONLY COOKIE SESSION HELPERS
# ------------------------------------------------------------------------------

def set_session_cookie(
    response: Response,
    token: str,
    max_age_seconds: Optional[int] = None,
) -> None:
    """
    Attaches the authentication session token to an HttpOnly, SameSite, Secure cookie.
    Prevents JavaScript/XSS access to the token.
    """
    if max_age_seconds is None:
        max_age_seconds = settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60

    response.set_cookie(
        key=settings.SESSION_COOKIE_NAME,
        value=token,
        max_age=max_age_seconds,
        expires=max_age_seconds,
        path="/",
        httponly=True,
        secure=settings.COOKIE_SECURE,
        samesite=settings.COOKIE_SAMESITE,
    )


def clear_session_cookie(response: Response) -> None:
    """
    Clears the HttpOnly session cookie on logout or invalid session.
    """
    response.delete_cookie(
        key=settings.SESSION_COOKIE_NAME,
        path="/",
        httponly=True,
        secure=settings.COOKIE_SECURE,
        samesite=settings.COOKIE_SAMESITE,
    )


def extract_session_token(request: Request) -> Optional[str]:
    """
    Extracts the session token from either:
    1. The primary HttpOnly cookie (`lifegraph_session`)
    2. Fallback: Authorization header `Bearer <token>` (for programmatic API callers)
    """
    # 1. Check HttpOnly cookie
    cookie_token = request.cookies.get(settings.SESSION_COOKIE_NAME)
    if cookie_token:
        return cookie_token

    # 2. Check Authorization Bearer header
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        return auth_header[7:].strip()

    return None


# ------------------------------------------------------------------------------
# 4. OAUTH CSRF STATE & NONCE COOKIE HELPERS
# ------------------------------------------------------------------------------

def set_oauth_state_cookie(
    response: Response,
    state: str,
    nonce: str,
) -> None:
    """
    Sets a short-lived (10-minute) HttpOnly cookie containing the CSRF state and nonce
    for Google OAuth 2.0 validation.
    Embeds an explicit server-side 'exp' claim (10 minutes) for tamper and replay prevention.
    """
    now = int(time.time())
    expires_at = now + 600  # 10 minutes
    state_payload = json.dumps(
        {"state": state, "nonce": nonce, "iat": now, "exp": expires_at},
        separators=(",", ":"),
    )
    encoded_state = base64.urlsafe_b64encode(state_payload.encode("utf-8")).decode("ascii").rstrip("=")

    response.set_cookie(
        key=settings.OAUTH_STATE_COOKIE_NAME,
        value=encoded_state,
        max_age=600,  # 10 minutes
        expires=600,
        path="/",
        httponly=True,
        secure=settings.COOKIE_SECURE,
        samesite="lax",
    )


def _parse_and_validate_state_payload(data: Any) -> Optional[Tuple[str, str]]:
    """
    Validates state payload dictionary:
    - Must be a dictionary.
    - 'exp' claim is strictly required: rejected if missing, null, malformed, or expired.
    - Legacy payloads without exp or delimiter-separated strings are strictly rejected.
    - 'state' and 'nonce' must be present, non-empty strings.
    """
    if not isinstance(data, dict):
        return None

    # Reject if exp claim is missing or None
    if "exp" not in data or data["exp"] is None:
        return None

    try:
        exp_val = float(data["exp"])
    except (ValueError, TypeError):
        return None  # Malformed exp rejected

    if time.time() > exp_val:
        return None  # Expired state rejected

    s = data.get("state")
    n = data.get("nonce")
    if (
        s and n
        and isinstance(s, str) and isinstance(n, str)
        and s.strip() and n.strip()
    ):
        return s.strip(), n.strip()

    return None


def get_oauth_state_from_cookie(request: Request) -> Optional[Tuple[str, str]]:
    """
    Retrieves and parses the state and nonce stored in the OAuth state cookie.
    Validates that:
    - 'exp' is present, non-null, valid numeric, and not expired (time.time() <= exp).
    - 'state' and 'nonce' are present and non-empty strings.
    - Legacy state payloads without exp or delimiter-separated formats are strictly rejected.
    Returns (state, nonce) or None.
    """
    raw = request.cookies.get(settings.OAUTH_STATE_COOKIE_NAME)
    if not raw:
        return None

    cleaned = raw.strip('"\'')
    if "%" in cleaned:
        cleaned = urllib.parse.unquote(cleaned).strip('"\'')

    # 1. Base64 URL-safe JSON decoding
    try:
        padded = cleaned + "=" * (-len(cleaned) % 4)
        decoded = base64.urlsafe_b64decode(padded.encode("ascii")).decode("utf-8")
        data = json.loads(decoded)
        result = _parse_and_validate_state_payload(data)
        if result:
            return result
    except Exception:
        pass

    # 2. Raw JSON string decoding
    try:
        data = json.loads(cleaned)
        result = _parse_and_validate_state_payload(data)
        if result:
            return result
    except Exception:
        pass

    # Legacy formats without explicit exp are strictly rejected
    return None


def clear_oauth_state_cookie(response: Response) -> None:
    """Clears the temporary OAuth state cookie."""
    response.delete_cookie(
        key=settings.OAUTH_STATE_COOKIE_NAME,
        path="/",
        httponly=True,
        secure=settings.COOKIE_SECURE,
        samesite="lax",
    )
