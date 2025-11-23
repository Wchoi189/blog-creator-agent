"""Authentication service"""

import uuid
from datetime import datetime, timedelta
from typing import Optional
from backend.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    generate_api_key,
    hash_api_key,
)
from backend.core.database import db
from backend.models.auth import UserCreate, User, Token, APIKeyCreate, APIKey


class AuthService:
    """Handles authentication logic"""

    def __init__(self):
        self.redis = db.redis

    async def register_user(self, user_data: UserCreate) -> User:
        """Register a new user"""
        user_id = str(uuid.uuid4())

        # Check if user exists
        existing_user = self.redis.hget("users:by_email", user_data.email)
        if existing_user:
            raise ValueError("User with this email already exists")

        # Create user
        user = {
            "id": user_id,
            "email": user_data.email,
            "full_name": user_data.full_name or "",
            "password_hash": hash_password(user_data.password),
            "created_at": datetime.utcnow().isoformat(),
            "is_active": "true",
        }

        # Store user
        self.redis.hset(f"user:{user_id}", mapping=user)
        self.redis.hset("users:by_email", user_data.email, user_id)

        return User(
            id=user_id,
            email=user_data.email,
            full_name=user_data.full_name,
            created_at=datetime.utcnow(),
            is_active=True,
        )

    async def authenticate_user(self, email: str, password: str) -> Optional[User]:
        """Authenticate a user"""
        # Get user ID by email
        user_id = self.redis.hget("users:by_email", email)
        if not user_id:
            return None

        # Get user data
        user_data = self.redis.hgetall(f"user:{user_id}")
        if not user_data:
            return None

        # Verify password
        if not verify_password(password, user_data["password_hash"]):
            return None

        return User(
            id=user_id,
            email=user_data["email"],
            full_name=user_data.get("full_name", ""),
            created_at=datetime.fromisoformat(user_data["created_at"]),
            is_active=user_data.get("is_active", "true") == "true",
        )

    async def create_tokens(self, user_id: str) -> Token:
        """Create access and refresh tokens"""
        access_token = create_access_token(data={"sub": user_id})
        refresh_token = create_refresh_token(data={"sub": user_id})

        return Token(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
        )

    async def get_user_by_id(self, user_id: str) -> Optional[User]:
        """Get user by ID"""
        user_data = self.redis.hgetall(f"user:{user_id}")
        if not user_data:
            return None

        return User(
            id=user_id,
            email=user_data["email"],
            full_name=user_data.get("full_name", ""),
            created_at=datetime.fromisoformat(user_data["created_at"]),
            is_active=user_data.get("is_active", "true") == "true",
        )

    async def create_api_key(self, user_id: str, key_data: APIKeyCreate) -> APIKey:
        """Create a new API key"""
        key_id = str(uuid.uuid4())
        api_key = generate_api_key()
        key_prefix = api_key[:10] + "..."

        # Calculate expiration
        expires_at = None
        if key_data.expires_in_days:
            expires_at = datetime.utcnow() + timedelta(days=key_data.expires_in_days)

        # Store API key
        key_obj = {
            "id": key_id,
            "user_id": user_id,
            "name": key_data.name,
            "key_hash": hash_api_key(api_key),
            "key_prefix": key_prefix,
            "created_at": datetime.utcnow().isoformat(),
            "expires_at": expires_at.isoformat() if expires_at else "",
            "last_used_at": "",
        }

        self.redis.hset(f"api_key:{key_id}", mapping=key_obj)
        self.redis.sadd(f"user:{user_id}:api_keys", key_id)

        return APIKey(
            id=key_id,
            name=key_data.name,
            key=api_key,  # Only shown once
            key_prefix=key_prefix,
            created_at=datetime.utcnow(),
            expires_at=expires_at,
        )

    async def list_api_keys(self, user_id: str) -> list:
        """List user's API keys"""
        key_ids = self.redis.smembers(f"user:{user_id}:api_keys")
        keys = []

        for key_id in key_ids:
            key_data = self.redis.hgetall(f"api_key:{key_id}")
            if key_data:
                keys.append({
                    "id": key_id,
                    "name": key_data["name"],
                    "key_prefix": key_data["key_prefix"],
                    "created_at": key_data["created_at"],
                    "expires_at": key_data.get("expires_at", ""),
                    "last_used_at": key_data.get("last_used_at", ""),
                })

        return keys

    async def revoke_api_key(self, user_id: str, key_id: str) -> bool:
        """Revoke an API key"""
        # Verify key belongs to user
        if not self.redis.sismember(f"user:{user_id}:api_keys", key_id):
            return False

        # Delete key
        self.redis.delete(f"api_key:{key_id}")
        self.redis.srem(f"user:{user_id}:api_keys", key_id)

        return True


# Global service instance
auth_service = AuthService()
