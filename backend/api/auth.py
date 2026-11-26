import re
import uuid
from datetime import timedelta
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Request, Response
from sqlalchemy.orm import Session
from sqlalchemy import func

from backend.database import get_db
from backend.models import User
from backend.schemas import (
    UserRegisterRequest,
    UserLoginRequest,
    UserResponse,
    AuthTokenResponse,
    MessageResponse,
)
from backend.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    decode_access_token,
    set_session_cookie,
    clear_session_cookie,
    extract_session_token,
)

router = APIRouter(prefix="/auth", tags=["Authentication"])

EMAIL_REGEX = re.compile(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")


# ------------------------------------------------------------------------------
# DEPENDENCY: GET CURRENT AUTHENTICATED USER
# ------------------------------------------------------------------------------

def get_current_user(request: Request, db: Session = Depends(get_db)) -> User:
    """
    Extracts and cryptographically validates the session token from either:
    1. The primary HttpOnly session cookie ('lifegraph_session')
    2. Fallback Authorization header 'Bearer <token>'

    Returns the authenticated User model instance or raises HTTP 401.
    """
    token = extract_session_token(request)
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication credentials were not provided. Please log in.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid, expired, or tampered session token. Please log in again.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Session token missing user identification claim.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User account no longer exists.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account has been deactivated.",
        )

    return user


# ------------------------------------------------------------------------------
# ENDPOINTS
# ------------------------------------------------------------------------------

@router.post(
    "/register",
    response_model=AuthTokenResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new user account",
)
def register(req: UserRegisterRequest, response: Response, db: Session = Depends(get_db)):
    """
    Registers a new user account:
    - Validates email format.
    - Rejects duplicate email addresses.
    - Hashes the password using secure bcrypt / PBKDF2.
    - Issues a session token and sets an HttpOnly cookie.
    """
    email = req.email.strip().lower()

    if not EMAIL_REGEX.match(email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid email address format.",
        )

    # Check for existing user
    existing_user = db.query(User).filter(func.lower(User.email) == email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="An account with this email address already exists.",
        )

    # Hash password securely
    hashed_pw = hash_password(req.password)

    # Create user
    new_user = User(
        id=str(uuid.uuid4()),
        email=email,
        full_name=req.full_name.strip(),
        hashed_password=hashed_pw,
        is_active=True,
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # Mint JWT access token
    token = create_access_token({
        "sub": str(new_user.id),
        "email": new_user.email,
        "name": new_user.full_name,
    })

    # Attach secure HttpOnly session cookie
    set_session_cookie(response, token)

    return AuthTokenResponse(
        access_token=token,
        token_type="bearer",
        user=UserResponse.from_orm(new_user),
    )


@router.post(
    "/login",
    response_model=AuthTokenResponse,
    summary="Authenticate with email and password",
)
def login(req: UserLoginRequest, response: Response, db: Session = Depends(get_db)):
    """
    Authenticates a user with email and password:
    - Verifies password hash using constant-time verification.
    - Issues a signed JWT access token.
    - Sets an HttpOnly, Secure, SameSite session cookie.
    """
    email = req.email.strip().lower()

    user = db.query(User).filter(func.lower(User.email) == email).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This account has been deactivated.",
        )

    if not verify_password(req.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Token expiration (longer if remember_me is requested)
    expires_delta = timedelta(days=7) if req.remember_me else None
    token = create_access_token(
        {
            "sub": str(user.id),
            "email": user.email,
            "name": user.full_name,
        },
        expires_delta=expires_delta,
    )

    # Set HttpOnly session cookie
    max_age_seconds = int(expires_delta.total_seconds()) if expires_delta else None
    set_session_cookie(response, token, max_age_seconds=max_age_seconds)

    return AuthTokenResponse(
        access_token=token,
        token_type="bearer",
        user=UserResponse.from_orm(user),
    )


@router.post(
    "/logout",
    response_model=MessageResponse,
    summary="Log out and invalidate session cookie",
)
def logout(response: Response):
    """
    Logs out the current user by clearing the HttpOnly session cookie.
    """
    clear_session_cookie(response)
    return MessageResponse(message="Successfully logged out.")


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Get current authenticated user profile",
)
def get_me(current_user: User = Depends(get_current_user)):
    """
    Returns the profile of the currently authenticated user.
    Rejects unauthenticated requests with HTTP 401.
    """
    return UserResponse.from_orm(current_user)
