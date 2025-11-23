"""Session API endpoints"""

from fastapi import APIRouter, Depends, HTTPException, status
from typing import List

from backend.models.sessions import Session, SessionCreate, SessionList, ChatHistory
from backend.services.session_service import session_service
from backend.core.security import get_current_user_id

router = APIRouter(prefix="/sessions", tags=["Sessions"])


@router.post("", response_model=Session, status_code=status.HTTP_201_CREATED)
async def create_session(
    session_data: SessionCreate,
    user_id: str = Depends(get_current_user_id),
):
    """Create a new session"""
    session = await session_service.create_session(user_id, session_data)
    return session


@router.get("", response_model=SessionList)
async def list_sessions(user_id: str = Depends(get_current_user_id)):
    """List user's sessions"""
    sessions = await session_service.list_sessions(user_id)
    return SessionList(sessions=sessions, total=len(sessions))


@router.get("/{session_id}", response_model=Session)
async def get_session(
    session_id: str,
    user_id: str = Depends(get_current_user_id),
):
    """Get session by ID"""
    session = await session_service.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    if session.user_id != user_id:
        raise HTTPException(status_code=403, detail="Access denied")

    return session


@router.delete("/{session_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_session(
    session_id: str,
    user_id: str = Depends(get_current_user_id),
):
    """Delete a session"""
    success = await session_service.delete_session(user_id, session_id)
    if not success:
        raise HTTPException(status_code=404, detail="Session not found")

    return None


@router.get("/{session_id}/chat-history", response_model=ChatHistory)
async def get_chat_history(
    session_id: str,
    user_id: str = Depends(get_current_user_id),
):
    """Get session chat history"""
    session = await session_service.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    if session.user_id != user_id:
        raise HTTPException(status_code=403, detail="Access denied")

    messages = await session_service.get_chat_history(session_id)
    return ChatHistory(session_id=session_id, messages=messages)
