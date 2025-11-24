"""Security utilities for authentication and authorization"""

from datetime import datetime, timedelta
from typing import Optional
import hashlib
import bcrypt
from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from backend.config import settings


def _normalize_secret(secret: str) -> bytes:
    """Pre-hash secrets so bcrypt always receives <=72 bytes."""
    return hashlib.sha256(secret.encode("utf-8")).digest()


def _raw_secret(secret: str) -> bytes:
    return secret.encode("utf-8")

# HTTP Bearer for JWT
security = HTTPBearer()


def hash_password(password: str) -> str:
    """Hash a password using bcrypt with SHA-256 pre-hashing to avoid 72B limit."""
    salt = bcrypt.gensalt()
    digest = _normalize_secret(password)
    return bcrypt.hashpw(digest, salt).decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password, supporting both SHA-256-prehashed and legacy bcrypt hashes."""
    hashed_bytes = hashed_password.encode("utf-8")

    digest = _normalize_secret(plain_password)
    if bcrypt.checkpw(digest, hashed_bytes):
        return True

    # Legacy fallback for hashes created before SHA-256 pre-hashing.
    try:
        raw = _raw_secret(plain_password)
    except UnicodeEncodeError:
        return False

    if len(raw) <= 72:
        try:
            return bcrypt.checkpw(raw, hashed_bytes)
        except ValueError:
            return False

    return False


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT access token"""
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire, "type": "access"})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def create_refresh_token(data: dict) -> str:
    """Create a JWT refresh token"""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "type": "refresh"})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def decode_token(token: str) -> dict:
    """Decode and verify a JWT token"""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_current_user_id(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> str:
    """Dependency to get current user ID from JWT token"""
    token = credentials.credentials
    payload = decode_token(token)

    user_id: str = payload.get("sub")
    token_type: str = payload.get("type")

    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if token_type != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token type",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user_id


def generate_api_key() -> str:
    """Generate a secure API key"""
    import secrets
    return f"bca_{secrets.token_urlsafe(32)}"


def hash_api_key(api_key: str) -> str:
    """Hash an API key for storage"""
    return hash_password(api_key)


def verify_api_key(plain_key: str, hashed_key: str) -> bool:
    """Verify an API key against a hash"""
    return verify_password(plain_key, hashed_key)
