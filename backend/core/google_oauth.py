"""
LifeGraph AI - Google OAuth 2.0 Server-Side Verification Module
Handles:
- Cryptographic state and nonce generation for CSRF and replay protection
- Proper cryptographic signature verification against Google's JSON Web Key Set (JWKS)
  using RSA-256 public keys (https://www.googleapis.com/oauth2/v3/certs)
- Strict validation of audience, issuer, expiration, email_verified, and nonce claims
- In-memory key caching with TTL to prevent redundant JWKS network fetches
- Development/testing mock support for isolated, offline unit testing
"""

import time
import secrets
from typing import Dict, Any, Tuple, Optional, List
import httpx

from backend.config import settings

# Google OAuth 2.0 Public Endpoints & Constants
GOOGLE_JWKS_URL = "https://www.googleapis.com/oauth2/v3/certs"
GOOGLE_TOKENINFO_URL = "https://oauth2.googleapis.com/tokeninfo"
GOOGLE_ISSUERS = ["accounts.google.com", "https://accounts.google.com"]

# In-memory cache for Google's public JWKS keys
_JWKS_CACHE: Dict[str, Any] = {"keys": [], "expires_at": 0}
_JWKS_CACHE_TTL_SECONDS = 3600  # Cache keys for 1 hour


def generate_oauth_state_and_nonce() -> Tuple[str, str]:
    """
    Generates a cryptographically strong random state token and nonce.
    - state: prevents Cross-Site Request Forgery (CSRF).
    - nonce: prevents token replay attacks.
    """
    state = secrets.token_urlsafe(32)
    nonce = secrets.token_urlsafe(32)
    return state, nonce


def fetch_google_jwks(jwks_url: str = GOOGLE_JWKS_URL) -> List[Dict[str, Any]]:
    """
    Fetches Google's public JSON Web Key Set (JWKS) containing active RSA public keys.
    Caches keys in memory with a 1-hour TTL.
    """
    now = time.time()
    if _JWKS_CACHE["keys"] and now < _JWKS_CACHE["expires_at"]:
        return _JWKS_CACHE["keys"]

    try:
        with httpx.Client(timeout=10.0) as client:
            resp = client.get(jwks_url)
            if resp.status_code == 200:
                data = resp.json()
                keys = data.get("keys", [])
                _JWKS_CACHE["keys"] = keys
                _JWKS_CACHE["expires_at"] = now + _JWKS_CACHE_TTL_SECONDS
                return keys
    except Exception as e:
        print(f"[LifeGraph AI] Warning: Unable to fetch Google JWKS: {e}")

    return _JWKS_CACHE["keys"]


def verify_google_id_token_jwks(
    id_token: str,
    jwks_keys: Optional[List[Dict[str, Any]]] = None,
) -> Dict[str, Any]:
    """
    Cryptographically verifies the RS256 signature of a Google ID token using
    the published RSA public keys from Google's JWKS.
    """
    import jwt

    # 1. Read unverified header to locate Key ID ('kid') and algorithm ('alg')
    header = jwt.get_unverified_header(id_token)
    kid = header.get("kid")
    alg = header.get("alg")

    if alg != "RS256":
        raise ValueError(f"Unsupported token algorithm: '{alg}'. Expected RS256.")

    if not kid:
        raise ValueError("Google ID token header missing 'kid' (Key ID).")

    # 2. Retrieve JWKS keys
    keys = jwks_keys if jwks_keys is not None else fetch_google_jwks()
    if not keys:
        raise ValueError("Could not retrieve Google JWKS public keys for signature verification.")

    # 3. Match the key corresponding to token's kid
    matching_key = None
    for k in keys:
        if k.get("kid") == kid:
            matching_key = k
            break

    if not matching_key:
        raise ValueError(f"Key ID '{kid}' not found in Google's active JWKS.")

    # 4. Construct RSA public key from JWK dictionary and verify cryptographic signature
    public_key = jwt.algorithms.RSAAlgorithm.from_jwk(matching_key)

    # 5. Decode and cryptographically verify signature, audience, and expiration
    decode_options = {
        "verify_signature": True,
        "verify_exp": True,
        "verify_aud": bool(settings.GOOGLE_CLIENT_ID),
    }

    claims = jwt.decode(
        id_token,
        key=public_key,
        algorithms=["RS256"],
        audience=settings.GOOGLE_CLIENT_ID if settings.GOOGLE_CLIENT_ID else None,
        options=decode_options,
    )

    return claims


def verify_google_id_token(
    id_token: str,
    expected_nonce: Optional[str] = None,
    allow_dev_mock: bool = False,
    custom_jwks: Optional[List[Dict[str, Any]]] = None,
) -> Dict[str, Any]:
    """
    Comprehensive cryptographic verification of a Google OAuth 2.0 ID token:
    1. Validates cryptographic RS256 signature against Google JWKS public RSA keys.
    2. Validates issuer (iss in ['accounts.google.com', 'https://accounts.google.com']).
    3. Validates audience (aud == GOOGLE_CLIENT_ID).
    4. Validates expiration (exp > current_time).
    5. Validates email_verified == True.
    6. Validates cryptographic nonce match if provided.

    Returns normalized user dictionary:
    {
        "google_id": "...",
        "email": "user@example.com",
        "name": "Jane Doe",
        "picture": "https://...",
        "email_verified": True
    }
    Raises ValueError on validation failure.
    """
    if not id_token or not isinstance(id_token, str):
        raise ValueError("Invalid Google ID token format.")

    # In production, dev mock tokens are STRICTLY PROHIBITED regardless of DEBUG or allow_dev_mock
    is_production = settings.ENVIRONMENT.lower() == "production"
    if id_token.startswith("dev-mock-google-token:"):
        if is_production:
            raise ValueError("Dev-mock Google tokens are strictly prohibited in production environments.")
        if settings.DEBUG or allow_dev_mock:
            parts = id_token.split(":")
            mock_email = parts[1] if len(parts) > 1 else "dev-user@lifegraph.local"
            mock_name = parts[2] if len(parts) > 2 else "Developer User"
            return {
                "google_id": f"mock-google-{hash(mock_email)}",
                "email": mock_email.lower().strip(),
                "name": mock_name,
                "picture": None,
                "email_verified": True,
            }

    # 1. Cryptographic JWKS Signature Verification
    claims = None
    try:
        claims = verify_google_id_token_jwks(id_token, jwks_keys=custom_jwks)
    except Exception as jwks_err:
        # Fallback to tokeninfo verification only if PyJWT RSA parsing fails
        # or if custom_jwks is not set and JWKS endpoint is unreachable
        if custom_jwks is None:
            try:
                with httpx.Client(timeout=10.0) as client:
                    resp = client.get(GOOGLE_TOKENINFO_URL, params={"id_token": id_token})
                    if resp.status_code == 200:
                        claims = resp.json()
            except Exception:
                pass

        if not claims:
            raise ValueError(f"Google ID token signature verification failed: {jwks_err}")

    # 2. Issuer verification
    issuer = claims.get("iss")
    if issuer not in GOOGLE_ISSUERS:
        raise ValueError(f"Invalid Google ID token issuer: '{issuer}'. Must be accounts.google.com.")

    # 3. Audience verification (if client ID configured)
    if settings.GOOGLE_CLIENT_ID:
        aud = claims.get("aud")
        if aud != settings.GOOGLE_CLIENT_ID:
            raise ValueError(f"Google ID token audience mismatch: expected '{settings.GOOGLE_CLIENT_ID}', got '{aud}'.")

    # 4. Expiration verification
    exp = claims.get("exp")
    if exp:
        try:
            if time.time() > float(exp):
                raise ValueError("Google ID token has expired.")
        except (ValueError, TypeError):
            pass

    # 5. Email verification check
    email_verified = claims.get("email_verified")
    if str(email_verified).lower() not in ("true", "1"):
        raise ValueError("Google account email is not verified by Google.")

    # 6. Nonce verification if expected: nonce MUST be present and MUST exactly match
    if expected_nonce:
        token_nonce = claims.get("nonce")
        if not token_nonce or token_nonce != expected_nonce:
            raise ValueError("OAuth nonce missing or mismatch: potential replay attack.")

    email = claims.get("email", "").lower().strip()
    if not email:
        raise ValueError("Google ID token missing email address claim.")

    return {
        "google_id": claims.get("sub"),
        "email": email,
        "name": claims.get("name") or claims.get("given_name") or email.split("@")[0],
        "picture": claims.get("picture"),
        "email_verified": True,
    }
