"""Authentication API endpoints"""

from fastapi import APIRouter, Depends, HTTPException, status
from backend.models.auth import (
    UserCreate,
    UserLogin,
    User,
    Token,
    APIKeyCreate,
    APIKey,
    APIKeyInfo,
)
from backend.services.auth_service import auth_service
from backend.core.security import get_current_user_id

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=User, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserCreate):
    """Register a new user"""
    try:
        user = await auth_service.register_user(user_data)
        return user
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/login", response_model=Token)
async def login(credentials: UserLogin):
    """Login with email and password"""
    user = await auth_service.authenticate_user(
        credentials.email, credentials.password
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )

    tokens = await auth_service.create_tokens(user.id)
    return tokens


@router.get("/me", response_model=User)
async def get_current_user(user_id: str = Depends(get_current_user_id)):
    """Get current authenticated user"""
    user = await auth_service.get_user_by_id(user_id)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    return user


@router.post("/api-keys", response_model=APIKey, status_code=status.HTTP_201_CREATED)
async def create_api_key(
    key_data: APIKeyCreate,
    user_id: str = Depends(get_current_user_id),
):
    """Create a new API key"""
    api_key = await auth_service.create_api_key(user_id, key_data)
    return api_key


@router.get("/api-keys", response_model=list[APIKeyInfo])
async def list_api_keys(user_id: str = Depends(get_current_user_id)):
    """List user's API keys"""
    keys = await auth_service.list_api_keys(user_id)
    return keys


@router.delete("/api-keys/{key_id}", status_code=status.HTTP_204_NO_CONTENT)
async def revoke_api_key(
    key_id: str,
    user_id: str = Depends(get_current_user_id),
):
    """Revoke an API key"""
    success = await auth_service.revoke_api_key(user_id, key_id)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="API key not found",
        )

    return None
