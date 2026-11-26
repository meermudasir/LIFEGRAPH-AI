"""
LifeGraph AI - Authentication API Test Suite
Validates registration, login, logout, /auth/me, cookie management, session isolation,
and dual-path (/auth and /api/auth) endpoint availability.
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from backend.main import app
from backend.database import Base, get_db
from backend.models import User

# Isolated in-memory SQLite engine for authentication tests
auth_test_engine = create_engine(
    "sqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
AuthTestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=auth_test_engine)


@pytest.fixture(autouse=True)
def setup_auth_db():
    """Create fresh tables for each test and isolate database sessions."""
    Base.metadata.create_all(bind=auth_test_engine)
    old_override = app.dependency_overrides.get(get_db)

    def override_get_db():
        db = AuthTestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    yield
    Base.metadata.drop_all(bind=auth_test_engine)
    if old_override is not None:
        app.dependency_overrides[get_db] = old_override
    else:
        app.dependency_overrides.pop(get_db, None)


@pytest.fixture
def client():
    return TestClient(app)


# ------------------------------------------------------------------------------
# 1. REGISTRATION TESTS
# ------------------------------------------------------------------------------

def test_register_user_success(client):
    """New user can successfully register and receive token + session cookie."""
    payload = {
        "full_name": "Dr. Elena Rostova",
        "email": "elena.rostova@lifegraph.ai",
        "password": "SecurePassword123!",
    }
    response = client.post("/auth/register", json=payload)
    assert response.status_code == 201
    data = response.json()

    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert "user" in data

    user = data["user"]
    assert user["email"] == "elena.rostova@lifegraph.ai"
    assert user["full_name"] == "Dr. Elena Rostova"
    assert user["is_active"] is True
    assert "id" in user
    assert "created_at" in user
    # Ensure sensitive credentials are never exposed
    assert "hashed_password" not in user
    assert "password" not in user

    # Session cookie must be set
    assert "set-cookie" in response.headers
    assert "lifegraph_session=" in response.headers["set-cookie"]


def test_register_duplicate_email_rejected(client):
    """Reject duplicate email registrations with HTTP 400."""
    payload = {
        "full_name": "First User",
        "email": "duplicate@example.com",
        "password": "Password12345!",
    }
    res1 = client.post("/auth/register", json=payload)
    assert res1.status_code == 201

    # Second registration with identical email (case-insensitive)
    payload2 = {
        "full_name": "Second User",
        "email": "DUPLICATE@example.com",
        "password": "Password12345!",
    }
    res2 = client.post("/auth/register", json=payload2)
    assert res2.status_code == 400
    assert "already exists" in res2.json()["detail"].lower()


def test_register_invalid_email_format_rejected(client):
    """Reject invalid email addresses with HTTP 400."""
    payload = {
        "full_name": "Invalid Email",
        "email": "not-an-email",
        "password": "Password12345!",
    }
    res = client.post("/auth/register", json=payload)
    assert res.status_code == 400
    assert "invalid email" in res.json()["detail"].lower()


def test_register_short_password_rejected(client):
    """Reject passwords shorter than 8 characters."""
    payload = {
        "full_name": "Short Password",
        "email": "short@example.com",
        "password": "short",
    }
    res = client.post("/auth/register", json=payload)
    assert res.status_code == 422  # Pydantic schema validation error


# ------------------------------------------------------------------------------
# 2. LOGIN TESTS
# ------------------------------------------------------------------------------

def test_login_success(client):
    """Existing user can log in with valid credentials."""
    # Register user first
    reg_payload = {
        "full_name": "Marcus Vance",
        "email": "marcus.vance@lifegraph.ai",
        "password": "VancePassword999!",
    }
    client.post("/auth/register", json=reg_payload)

    # Login
    login_payload = {
        "email": "marcus.vance@lifegraph.ai",
        "password": "VancePassword999!",
        "remember_me": False,
    }
    response = client.post("/auth/login", json=login_payload)
    assert response.status_code == 200
    data = response.json()

    assert "access_token" in data
    assert data["user"]["email"] == "marcus.vance@lifegraph.ai"
    assert data["user"]["full_name"] == "Marcus Vance"
    assert "lifegraph_session=" in response.headers.get("set-cookie", "")


def test_login_case_insensitive_email(client):
    """Login succeeds when email casing differs from registration."""
    reg_payload = {
        "full_name": "Case Test",
        "email": "casetest@example.com",
        "password": "Password123!",
    }
    client.post("/auth/register", json=reg_payload)

    login_payload = {
        "email": "CASETEST@EXAMPLE.COM",
        "password": "Password123!",
    }
    response = client.post("/auth/login", json=login_payload)
    assert response.status_code == 200


def test_login_wrong_password_rejected(client):
    """Reject login attempts with invalid password."""
    reg_payload = {
        "full_name": "Wrong Pw User",
        "email": "wrongpw@example.com",
        "password": "CorrectPassword123!",
    }
    client.post("/auth/register", json=reg_payload)

    login_payload = {
        "email": "wrongpw@example.com",
        "password": "IncorrectPassword999!",
    }
    response = client.post("/auth/login", json=login_payload)
    assert response.status_code == 401
    assert "invalid email or password" in response.json()["detail"].lower()


def test_login_nonexistent_user_rejected(client):
    """Reject login attempts for non-existent users."""
    login_payload = {
        "email": "ghost@example.com",
        "password": "GhostPassword123!",
    }
    response = client.post("/auth/login", json=login_payload)
    assert response.status_code == 401
    assert "invalid email or password" in response.json()["detail"].lower()


def test_login_remember_me_extended_cookie(client):
    """Remember Me extends cookie lifetime."""
    reg_payload = {
        "full_name": "Remember Me User",
        "email": "remember@example.com",
        "password": "Password123!",
    }
    client.post("/auth/register", json=reg_payload)

    login_payload = {
        "email": "remember@example.com",
        "password": "Password123!",
        "remember_me": True,
    }
    response = client.post("/auth/login", json=login_payload)
    assert response.status_code == 200
    cookie_header = response.headers.get("set-cookie", "")
    assert "lifegraph_session=" in cookie_header
    # 7 days = 604800 seconds
    assert "max-age=604800" in cookie_header.lower()


# ------------------------------------------------------------------------------
# 3. GET /auth/me & PROFILE ISOLATION TESTS
# ------------------------------------------------------------------------------

def test_get_me_unauthenticated_rejected(client):
    """Unauthenticated requests to /auth/me return HTTP 401."""
    response = client.get("/auth/me")
    assert response.status_code == 401
    assert "WWW-Authenticate" in response.headers


def test_get_me_authenticated_via_cookie(client):
    """User profile is retrieved using the session cookie."""
    reg_payload = {
        "full_name": "Cookie User",
        "email": "cookie.user@lifegraph.ai",
        "password": "CookiePassword123!",
    }
    reg_res = client.post("/auth/register", json=reg_payload)
    token = reg_res.json()["access_token"]

    # Supply cookie
    client.cookies.set("lifegraph_session", token)
    response = client.get("/auth/me")
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "cookie.user@lifegraph.ai"
    assert data["full_name"] == "Cookie User"


def test_get_me_authenticated_via_bearer_header(client):
    """User profile is retrieved using Authorization: Bearer <token> header."""
    reg_payload = {
        "full_name": "Header User",
        "email": "header.user@lifegraph.ai",
        "password": "HeaderPassword123!",
    }
    reg_res = client.post("/auth/register", json=reg_payload)
    token = reg_res.json()["access_token"]

    headers = {"Authorization": f"Bearer {token}"}
    response = client.get("/auth/me", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "header.user@lifegraph.ai"


def test_get_me_invalid_token_rejected(client):
    """Bogus or tampered tokens return HTTP 401."""
    headers = {"Authorization": "Bearer invalid.jwt.token"}
    response = client.get("/auth/me", headers=headers)
    assert response.status_code == 401


def test_user_session_and_profile_isolation(client):
    """Each user's session returns strictly their own isolated profile."""
    # User A
    res_a = client.post("/auth/register", json={
        "full_name": "User Alpha",
        "email": "alpha@example.com",
        "password": "AlphaPassword123!",
    })
    token_a = res_a.json()["access_token"]

    # User B
    res_b = client.post("/auth/register", json={
        "full_name": "User Beta",
        "email": "beta@example.com",
        "password": "BetaPassword123!",
    })
    token_b = res_b.json()["access_token"]

    # Verify A gets Alpha profile
    client.cookies.set("lifegraph_session", token_a)
    me_a = client.get("/auth/me").json()
    assert me_a["email"] == "alpha@example.com"
    assert me_a["full_name"] == "User Alpha"

    # Verify B gets Beta profile
    client.cookies.set("lifegraph_session", token_b)
    me_b = client.get("/auth/me").json()
    assert me_b["email"] == "beta@example.com"
    assert me_b["full_name"] == "User Beta"

    # Confirm IDs are distinct and neither profile overlaps
    assert me_a["id"] != me_b["id"]


# ------------------------------------------------------------------------------
# 4. LOGOUT TESTS
# ------------------------------------------------------------------------------

def test_logout_clears_session_cookie(client):
    """Logout invalidates and clears the session cookie."""
    response = client.post("/auth/logout")
    assert response.status_code == 200
    assert "successfully logged out" in response.json()["message"].lower()

    # Cookie must be cleared (Max-Age=0 or empty value)
    cookie_header = response.headers.get("set-cookie", "")
    assert "lifegraph_session=" in cookie_header
    assert "max-age=0" in cookie_header.lower()


# ------------------------------------------------------------------------------
# 5. DUAL PATH ROUTING COMPATIBILITY (/auth and /api/auth)
# ------------------------------------------------------------------------------

def test_dual_path_routing_api_prefix(client):
    """Verify that both /auth/* and /api/auth/* endpoints respond correctly."""
    # Register via /api/auth/register
    reg_payload = {
        "full_name": "API Prefix User",
        "email": "api.prefix@lifegraph.ai",
        "password": "ApiPassword123!",
    }
    reg_res = client.post("/api/auth/register", json=reg_payload)
    assert reg_res.status_code == 201

    # Login via /api/auth/login
    login_payload = {
        "email": "api.prefix@lifegraph.ai",
        "password": "ApiPassword123!",
    }
    login_res = client.post("/api/auth/login", json=login_payload)
    assert login_res.status_code == 200
    token = login_res.json()["access_token"]

    # Get /api/auth/me
    headers = {"Authorization": f"Bearer {token}"}
    me_res = client.get("/api/auth/me", headers=headers)
    assert me_res.status_code == 200
    assert me_res.json()["email"] == "api.prefix@lifegraph.ai"

    # Logout via /api/auth/logout
    logout_res = client.post("/api/auth/logout")
    assert logout_res.status_code == 200


# ------------------------------------------------------------------------------
# 6. CORS & CREDENTIALS INTEGRATION TESTS
# ------------------------------------------------------------------------------

def test_cors_preflight_and_credentials_frontend_origin(client):
    """
    Verify CORS preflight OPTIONS and credentials header support for local frontend servers
    (e.g., Live Server on http://127.0.0.1:5500 and http://localhost:5500).
    """
    origins_to_test = ["http://127.0.0.1:5500", "http://localhost:5500"]

    for origin in origins_to_test:
        # Preflight OPTIONS request
        options_res = client.options(
            "/auth/me",
            headers={
                "Origin": origin,
                "Access-Control-Request-Method": "GET",
                "Access-Control-Request-Headers": "Authorization,Content-Type",
            },
        )
        assert options_res.status_code == 200
        assert options_res.headers.get("access-control-allow-origin") == origin
        assert options_res.headers.get("access-control-allow-credentials") == "true"

        # Actual GET request with Origin
        get_res = client.get(
            "/auth/me",
            headers={"Origin": origin},
        )
        # Even when 401 unauthenticated, CORS headers must be present so browser doesn't throw CORS error
        assert get_res.status_code == 401
        assert get_res.headers.get("access-control-allow-origin") == origin
        assert get_res.headers.get("access-control-allow-credentials") == "true"


# ------------------------------------------------------------------------------
# 7. COMPLETE AUTHENTICATION VERIFICATION & PERSISTENCE TESTS
# ------------------------------------------------------------------------------

def test_page_refresh_preserves_authentication(client):
    """
    Simulates page reload / revisit:
    After successful login, both cookie and stored access_token repeatedly authenticate
    subsequent requests to /auth/me without re-prompting for credentials.
    """
    # 1. Register and login
    reg_payload = {
        "full_name": "Persistent User",
        "email": "persistent@lifegraph.ai",
        "password": "PersistentPassword123!",
    }
    client.post("/auth/register", json=reg_payload)

    login_res = client.post("/auth/login", json={
        "email": "persistent@lifegraph.ai",
        "password": "PersistentPassword123!",
    })
    assert login_res.status_code == 200
    token = login_res.json()["access_token"]

    # 2. Simulate 3 consecutive page refreshes using Bearer header (as stored in localStorage)
    headers = {"Authorization": f"Bearer {token}"}
    for _ in range(3):
        refresh_res = client.get("/auth/me", headers=headers)
        assert refresh_res.status_code == 200
        user_data = refresh_res.json()
        assert user_data["email"] == "persistent@lifegraph.ai"
        assert user_data["full_name"] == "Persistent User"
        assert user_data["is_active"] is True

    # 3. Simulate 3 consecutive page refreshes using HttpOnly cookie (as stored in browser)
    client.cookies.set("lifegraph_session", token)
    for _ in range(3):
        cookie_refresh_res = client.get("/auth/me")
        assert cookie_refresh_res.status_code == 200
        assert cookie_refresh_res.json()["email"] == "persistent@lifegraph.ai"


def test_unauthenticated_guest_state_clean_401(client):
    """
    Verify unauthenticated requests return a clean HTTP 401 with standard detail and
    WWW-Authenticate header, allowing frontend to render Guest Explorer without exceptions.
    """
    client.cookies.clear()
    res = client.get("/auth/me")
    assert res.status_code == 401
    assert res.headers.get("www-authenticate") == "Bearer"
    assert "detail" in res.json()
    assert "log in" in res.json()["detail"].lower()


def test_backend_startup_and_health_probes(client):
    """
    Verify backend root and health endpoints confirm startup readiness.
    """
    root_res = client.get("/")
    assert root_res.status_code == 200
    assert root_res.json()["status"] == "online"

    health_res = client.get("/health")
    assert health_res.status_code == 200
    assert health_res.json()["status"] == "healthy"
