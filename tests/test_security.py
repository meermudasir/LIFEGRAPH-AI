"""
LifeGraph AI - Stage 1 Security & Authentication Unit Test Suite
Verifies:
1. Password hashing uniqueness and verification
2. Password rejection on incorrect password
3. Empty password rejection
4. JWT token creation and correct decoding
5. Expired JWT token rejection
6. Tampered JWT signature rejection
7. HttpOnly, SameSite, Secure session cookie management
8. OAuth state and nonce generation for CSRF protection
9. Google ID token parsing and mock verification
10. Google OAuth cryptographic RS256 signature verification via JWKS
11. Environment configuration settings and security flags
"""

import time
import json
from datetime import timedelta
import pytest
from fastapi import Response, Request

from backend.config import settings
from backend.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    decode_access_token,
    set_session_cookie,
    clear_session_cookie,
    extract_session_token,
    set_oauth_state_cookie,
    get_oauth_state_from_cookie,
    clear_oauth_state_cookie,
    PBKDF2_RECOMMENDED_ITERATIONS,
)
from backend.core.google_oauth import (
    generate_oauth_state_and_nonce,
    verify_google_id_token,
    verify_google_id_token_jwks,
)


# ------------------------------------------------------------------------------
# 1. PASSWORD HASHING TESTS
# ------------------------------------------------------------------------------

def test_password_hashing_and_verification():
    """Verify that a plain-text password can be hashed and verified."""
    raw_password = "SuperSecretPassword123!"
    hashed = hash_password(raw_password)

    assert hashed != raw_password
    assert len(hashed) > 20
    assert verify_password(raw_password, hashed) is True


def test_password_verification_fails_on_wrong_password():
    """Verify that an incorrect password fails verification."""
    raw_password = "CorrectPassword123!"
    hashed = hash_password(raw_password)

    assert verify_password("WrongPassword123!", hashed) is False
    assert verify_password("correctpassword123!", hashed) is False
    assert verify_password("", hashed) is False


def test_password_hashing_unique_salts():
    """Verify that hashing the same password twice yields different hashes (random salting)."""
    raw_password = "TestPassword456"
    hash1 = hash_password(raw_password)
    hash2 = hash_password(raw_password)

    assert hash1 != hash2
    assert verify_password(raw_password, hash1) is True
    assert verify_password(raw_password, hash2) is True


def test_empty_password_raises_error():
    """Verify that empty password strings are rejected."""
    with pytest.raises(ValueError):
        hash_password("")


# ------------------------------------------------------------------------------
# 2. JWT TOKEN GENERATION & VERIFICATION TESTS
# ------------------------------------------------------------------------------

def test_jwt_token_creation_and_decoding():
    """Verify standard JWT token creation and successful claim decoding."""
    payload_data = {"sub": "user_uuid_12345", "email": "test@lifegraph.local", "role": "admin"}
    token = create_access_token(payload_data)

    assert isinstance(token, str)
    assert len(token.split(".")) == 3

    decoded = decode_access_token(token)
    assert decoded is not None
    assert decoded["sub"] == "user_uuid_12345"
    assert decoded["email"] == "test@lifegraph.local"
    assert decoded["role"] == "admin"
    assert "exp" in decoded
    assert "iat" in decoded


def test_jwt_token_expiration_rejection():
    """Verify that an expired token returns None upon decoding."""
    payload_data = {"sub": "user_expired_999"}
    # Token expired 10 seconds ago
    expired_token = create_access_token(payload_data, expires_delta=timedelta(seconds=-10))

    decoded = decode_access_token(expired_token)
    assert decoded is None


def test_jwt_tampered_signature_rejection():
    """Verify that modifying the payload or signature causes rejection."""
    payload_data = {"sub": "user_honest"}
    token = create_access_token(payload_data)
    parts = token.split(".")

    # Tamper with signature
    tampered_sig = parts[2][:-4] + "xxxx"
    tampered_token = f"{parts[0]}.{parts[1]}.{tampered_sig}"

    assert decode_access_token(tampered_token) is None


def test_invalid_token_strings():
    """Verify that malformed token strings are rejected without crashing."""
    assert decode_access_token("") is None
    assert decode_access_token("not-a-token") is None
    assert decode_access_token("a.b") is None
    assert decode_access_token(None) is None


def test_jwt_missing_or_empty_sub_rejected():
    """Verify that tokens missing a valid, non-empty subject claim ('sub') are rejected."""
    # 1. Token without sub
    token_no_sub = create_access_token({"email": "nosub@example.com", "role": "user"})
    assert decode_access_token(token_no_sub) is None

    # 2. Token with empty sub
    token_empty_sub = create_access_token({"sub": "", "email": "empty@example.com"})
    assert decode_access_token(token_empty_sub) is None

    # 3. Token with whitespace sub
    token_whitespace_sub = create_access_token({"sub": "   ", "email": "ws@example.com"})
    assert decode_access_token(token_whitespace_sub) is None

    # 4. Token with None sub
    token_none_sub = create_access_token({"sub": None, "email": "none@example.com"})
    assert decode_access_token(token_none_sub) is None


# ------------------------------------------------------------------------------
# 3. HTTPONLY SESSION COOKIE TESTS
# ------------------------------------------------------------------------------

def test_set_and_clear_session_cookie():
    """Verify that session cookies are set with HttpOnly and correct path."""
    response = Response()
    fake_token = "header.payload.signature"

    set_session_cookie(response, fake_token)
    set_cookie_headers = [
        val for k, val in response.raw_headers if k.decode("latin-1").lower() == "set-cookie"
    ]

    assert len(set_cookie_headers) >= 1
    cookie_str = set_cookie_headers[0].decode("latin-1")
    assert settings.SESSION_COOKIE_NAME in cookie_str
    assert fake_token in cookie_str
    assert "HttpOnly" in cookie_str or "httponly" in cookie_str
    assert "Path=/" in cookie_str or "path=/" in cookie_str

    # Test clear
    clear_response = Response()
    clear_session_cookie(clear_response)
    clear_cookie_headers = [
        val for k, val in clear_response.raw_headers if k.decode("latin-1").lower() == "set-cookie"
    ]
    assert len(clear_cookie_headers) >= 1
    clear_str = clear_cookie_headers[0].decode("latin-1")
    assert settings.SESSION_COOKIE_NAME in clear_str
    assert 'max-age=0' in clear_str.lower() or 'expires=' in clear_str.lower()


def test_extract_session_token_from_cookie():
    """Verify extracting token from request cookies."""
    scope = {
        "type": "http",
        "headers": [(b"cookie", f"{settings.SESSION_COOKIE_NAME}=token_abc_123".encode())],
    }
    request = Request(scope)
    extracted = extract_session_token(request)
    assert extracted == "token_abc_123"


def test_extract_session_token_from_bearer_header_fallback():
    """Verify fallback extraction from Authorization: Bearer <token> header."""
    scope = {
        "type": "http",
        "headers": [(b"authorization", b"Bearer header_token_xyz_789")],
    }
    request = Request(scope)
    extracted = extract_session_token(request)
    assert extracted == "header_token_xyz_789"


# ------------------------------------------------------------------------------
# 4. OAUTH CSRF STATE & NONCE TESTS
# ------------------------------------------------------------------------------

def test_oauth_state_and_nonce_generation():
    """Verify generation of distinct high-entropy state and nonce tokens."""
    state1, nonce1 = generate_oauth_state_and_nonce()
    state2, nonce2 = generate_oauth_state_and_nonce()

    assert len(state1) >= 32
    assert len(nonce1) >= 32
    assert state1 != nonce1
    assert state1 != state2
    assert nonce1 != nonce2


def test_oauth_state_cookie_roundtrip():
    """Verify setting and reading the OAuth state/nonce cookie."""
    state, nonce = generate_oauth_state_and_nonce()
    response = Response()
    set_oauth_state_cookie(response, state, nonce)

    # Extract the cookie from response headers to simulate client returning it
    set_cookie_headers = [
        val for k, val in response.raw_headers if k.decode("latin-1").lower() == "set-cookie"
    ]
    raw_header = set_cookie_headers[0].decode("latin-1")
    cookie_part = raw_header.split(";")[0]
    cookie_value = cookie_part.split("=", 1)[1].strip('"')

    # Simulate incoming request
    scope = {
        "type": "http",
        "headers": [(b"cookie", f"{settings.OAUTH_STATE_COOKIE_NAME}={cookie_value}".encode())],
    }
    request = Request(scope)
    parsed = get_oauth_state_from_cookie(request)

    assert parsed is not None
    extracted_state, extracted_nonce = parsed
    assert extracted_state == state
    assert extracted_nonce == nonce


# ------------------------------------------------------------------------------
# 5. GOOGLE OAUTH CRYPTOGRAPHIC & JWKS VERIFICATION TESTS
# ------------------------------------------------------------------------------

def test_google_id_token_dev_mock():
    """Verify dev mock token verification for testing and local development."""
    mock_token = "dev-mock-google-token:alice@university.edu:Alice Turing"
    user_info = verify_google_id_token(mock_token, allow_dev_mock=True)

    assert user_info["email"] == "alice@university.edu"
    assert user_info["name"] == "Alice Turing"
    assert user_info["email_verified"] is True
    assert "google_id" in user_info


def test_google_id_token_empty_fails():
    """Verify empty or invalid token format raises ValueError."""
    with pytest.raises(ValueError):
        verify_google_id_token("")

    with pytest.raises(ValueError):
        verify_google_id_token(None)


def test_google_id_token_jwks_cryptographic_verification():
    """
    Verifies that Google OAuth tokens are verified using true RS256 cryptographic
    signatures against matching RSA public keys in the JWKS.
    """
    try:
        from cryptography.hazmat.primitives.asymmetric import rsa
        import jwt
    except ImportError:
        pytest.skip("cryptography or PyJWT not installed in test environment")

    # 1. Generate an RSA key pair for testing JWKS signature verification
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    public_key = private_key.public_key()

    # 2. Convert public key to JWK format
    jwk_dict = json.loads(jwt.algorithms.RSAAlgorithm.to_jwk(public_key))
    jwk_dict["kid"] = "test-google-key-id-01"
    jwk_dict["use"] = "sig"
    jwk_dict["alg"] = "RS256"

    # 3. Mint an ID token signed with RS256 private key
    now = int(time.time())
    token_claims = {
        "iss": "https://accounts.google.com",
        "sub": "google-user-987654321",
        "email": "researcher@lifegraph.ai",
        "name": "Dr. Researcher",
        "email_verified": True,
        "aud": settings.GOOGLE_CLIENT_ID if settings.GOOGLE_CLIENT_ID else "test-client-id",
        "exp": now + 3600,
        "iat": now,
        "nonce": "secure-nonce-xyz-123",
    }
    headers = {"kid": "test-google-key-id-01", "alg": "RS256"}
    signed_id_token = jwt.encode(token_claims, private_key, algorithm="RS256", headers=headers)

    # 4. Verify valid token against custom JWKS list
    orig_client_id = settings.GOOGLE_CLIENT_ID
    try:
        settings.GOOGLE_CLIENT_ID = "test-client-id"
        result = verify_google_id_token(
            signed_id_token,
            expected_nonce="secure-nonce-xyz-123",
            custom_jwks=[jwk_dict],
        )

        assert result["email"] == "researcher@lifegraph.ai"
        assert result["name"] == "Dr. Researcher"
        assert result["google_id"] == "google-user-987654321"
        assert result["email_verified"] is True

        # 5. Nonce mismatch must fail
        with pytest.raises(ValueError, match="OAuth nonce missing or mismatch"):
            verify_google_id_token(
                signed_id_token,
                expected_nonce="wrong-nonce",
                custom_jwks=[jwk_dict],
            )

        # 6. Tampered signature must fail cryptographic verification
        tampered_token = signed_id_token[:-5] + "aaaaa"
        with pytest.raises(ValueError, match="signature verification failed"):
            verify_google_id_token(
                tampered_token,
                expected_nonce="secure-nonce-xyz-123",
                custom_jwks=[jwk_dict],
            )
    finally:
        settings.GOOGLE_CLIENT_ID = orig_client_id


# ------------------------------------------------------------------------------
# 6. CONFIGURATION SETTINGS TESTS
# ------------------------------------------------------------------------------

def test_settings_security_defaults():
    """Verify security configuration settings are loaded with sensible defaults."""
    assert settings.SECRET_KEY != ""
    assert settings.ALGORITHM == "HS256"
    assert settings.ACCESS_TOKEN_EXPIRE_MINUTES > 0
    assert settings.SESSION_COOKIE_NAME == "lifegraph_session"
    assert settings.OAUTH_STATE_COOKIE_NAME == "lifegraph_oauth_state"
    assert settings.LEGACY_OWNER_EMAIL == "admin@lifegraph.local"
    assert settings.LEGACY_OWNER_NAME != ""


# ------------------------------------------------------------------------------
# 7. PRODUCTION SECURITY HARDENING TESTS
# ------------------------------------------------------------------------------

def test_production_secret_key_validation_fails_on_default_or_insecure():
    """Verify production startup validation rejects default, missing, or short keys."""
    orig_env = settings.ENVIRONMENT
    orig_key = settings.SECRET_KEY

    try:
        settings.ENVIRONMENT = "production"
        # 1. Default dev key must be rejected
        settings.SECRET_KEY = settings.DEFAULT_DEV_SECRET_KEY
        with pytest.raises(RuntimeError, match="Production startup aborted"):
            settings.validate_production_security()

        # 2. Empty key must be rejected
        settings.SECRET_KEY = ""
        with pytest.raises(RuntimeError, match="Production startup aborted"):
            settings.validate_production_security()

        # 3. Short key (<32 chars) must be rejected
        settings.SECRET_KEY = "too_short_key_123"
        with pytest.raises(RuntimeError, match="Production startup aborted"):
            settings.validate_production_security()

        # 4. Strong key (>=32 chars) passes validation
        settings.SECRET_KEY = "a-very-secure-random-production-key-at-least-32-chars-long"
        settings.validate_production_security()  # Should not raise
    finally:
        settings.ENVIRONMENT = orig_env
        settings.SECRET_KEY = orig_key


def test_dev_mock_google_token_strictly_rejected_in_production():
    """Verify dev mock tokens are completely prohibited in production, even if requested."""
    orig_env = settings.ENVIRONMENT
    try:
        settings.ENVIRONMENT = "production"
        mock_token = "dev-mock-google-token:admin@company.com:Admin"

        with pytest.raises(ValueError, match="strictly prohibited in production"):
            verify_google_id_token(mock_token, allow_dev_mock=True)
    finally:
        settings.ENVIRONMENT = orig_env


def test_jwt_issuer_validation_rejection():
    """Verify that JWT tokens with invalid/tampered issuer are strictly rejected."""
    import jwt

    now = int(time.time())
    invalid_claims = {
        "sub": "user_tampered_issuer",
        "email": "hacker@evil.corp",
        "exp": now + 3600,
        "iat": now,
        "iss": "untrusted-issuer",
    }
    # Encode with the correct secret key but wrong issuer
    forged_token = jwt.encode(invalid_claims, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

    decoded = decode_access_token(forged_token)
    assert decoded is None


def test_google_oauth_nonce_missing_rejected_when_expected():
    """Verify that if nonce is expected, a token missing the nonce claim is rejected."""
    try:
        from cryptography.hazmat.primitives.asymmetric import rsa
        import jwt
    except ImportError:
        pytest.skip("cryptography or PyJWT not installed")

    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    jwk_dict = json.loads(jwt.algorithms.RSAAlgorithm.to_jwk(private_key.public_key()))
    jwk_dict["kid"] = "nonce-test-kid"
    jwk_dict["alg"] = "RS256"

    now = int(time.time())
    # Omit "nonce" claim
    claims_no_nonce = {
        "iss": "https://accounts.google.com",
        "sub": "google-user-no-nonce",
        "email": "user@lifegraph.ai",
        "email_verified": True,
        "aud": "test-client-id",
        "exp": now + 3600,
        "iat": now,
    }
    signed_token = jwt.encode(
        claims_no_nonce,
        private_key,
        algorithm="RS256",
        headers={"kid": "nonce-test-kid", "alg": "RS256"},
    )

    orig_client_id = settings.GOOGLE_CLIENT_ID
    try:
        settings.GOOGLE_CLIENT_ID = "test-client-id"
        with pytest.raises(ValueError, match="OAuth nonce missing or mismatch"):
            verify_google_id_token(
                signed_token,
                expected_nonce="expected-super-secret-nonce",
                custom_jwks=[jwk_dict],
            )
    finally:
        settings.GOOGLE_CLIENT_ID = orig_client_id


def test_oauth_state_cookie_expired_rejection():
    """Verify that an OAuth state cookie with an expired timestamp is rejected."""
    import base64

    now = int(time.time())
    # Create an expired payload (expired 5 minutes ago)
    expired_payload = {
        "state": "valid-state-value",
        "nonce": "valid-nonce-value",
        "iat": now - 900,
        "exp": now - 300,
    }
    encoded = base64.urlsafe_b64encode(json.dumps(expired_payload).encode()).decode()

    scope = {
        "type": "http",
        "headers": [(b"cookie", f"{settings.OAUTH_STATE_COOKIE_NAME}={encoded}".encode())],
    }
    request = Request(scope)
    parsed = get_oauth_state_from_cookie(request)
    assert parsed is None


def test_oauth_state_cookie_missing_exp_rejected():
    """Verify state payload without 'exp' is rejected (no legacy unexpired payloads)."""
    import base64
    payload_no_exp = {"state": "valid-state-abc", "nonce": "valid-nonce-xyz"}
    encoded = base64.urlsafe_b64encode(json.dumps(payload_no_exp).encode()).decode()

    scope = {
        "type": "http",
        "headers": [(b"cookie", f"{settings.OAUTH_STATE_COOKIE_NAME}={encoded}".encode())],
    }
    request = Request(scope)
    assert get_oauth_state_from_cookie(request) is None


def test_oauth_state_cookie_null_exp_rejected():
    """Verify state payload with exp=None is rejected."""
    import base64
    payload_null_exp = {"state": "valid-state-abc", "nonce": "valid-nonce-xyz", "exp": None}
    encoded = base64.urlsafe_b64encode(json.dumps(payload_null_exp).encode()).decode()

    scope = {
        "type": "http",
        "headers": [(b"cookie", f"{settings.OAUTH_STATE_COOKIE_NAME}={encoded}".encode())],
    }
    request = Request(scope)
    assert get_oauth_state_from_cookie(request) is None


def test_oauth_state_cookie_malformed_exp_rejected():
    """Verify state payload with malformed/non-numeric exp is rejected."""
    import base64
    for malformed_exp in ["not-a-number", [], {}]:
        payload = {"state": "valid-state-abc", "nonce": "valid-nonce-xyz", "exp": malformed_exp}
        encoded = base64.urlsafe_b64encode(json.dumps(payload).encode()).decode()

        scope = {
            "type": "http",
            "headers": [(b"cookie", f"{settings.OAUTH_STATE_COOKIE_NAME}={encoded}".encode())],
        }
        request = Request(scope)
        assert get_oauth_state_from_cookie(request) is None


def test_oauth_state_cookie_legacy_delimiter_format_rejected():
    """Verify legacy delimiter-separated formats ('state:nonce') are rejected."""
    scope = {
        "type": "http",
        "headers": [(b"cookie", f"{settings.OAUTH_STATE_COOKIE_NAME}=somestate:somenonce".encode())],
    }
    request = Request(scope)
    assert get_oauth_state_from_cookie(request) is None


def test_production_cookie_secure_enforced_even_if_configured_false():
    """Verify COOKIE_SECURE is strictly True in production, even if configured False."""
    orig_env = settings.ENVIRONMENT
    orig_secure = settings._cookie_secure_raw
    try:
        settings.ENVIRONMENT = "production"
        settings.COOKIE_SECURE = False  # Explicitly attempt to set False
        assert settings.COOKIE_SECURE is True
    finally:
        settings.ENVIRONMENT = orig_env
        settings._cookie_secure_raw = orig_secure


def test_pbkdf2_existing_100k_hash_verification_compatibility():
    """Verify backward compatibility: existing hashes with 100,000 rounds still verify."""
    import hashlib
    import secrets
    from backend.core.security import PBKDF2_RECOMMENDED_ITERATIONS

    raw_password = "LegacySecurePassword2024!"
    salt = secrets.token_hex(16)
    key_100k = hashlib.pbkdf2_hmac("sha256", raw_password.encode("utf-8"), salt.encode("utf-8"), 100_000)
    legacy_hash_100k = f"$pbkdf2$100000${salt}${key_100k.hex()}"

    assert verify_password(raw_password, legacy_hash_100k) is True
    assert verify_password("WrongPassword!", legacy_hash_100k) is False
    assert PBKDF2_RECOMMENDED_ITERATIONS == 600_000
