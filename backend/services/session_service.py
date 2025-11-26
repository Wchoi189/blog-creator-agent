"""Session management service"""

import uuid
import json
from datetime import datetime
from typing import Optional, List

from backend.core.database import db
from backend.models.sessions import Session, SessionCreate, ChatMessage


class SessionService:
    """Handles user session management"""

    def __init__(self):
        self.redis = db.redis

    async def create_session(
        self,
        user_id: str,
        session_data: SessionCreate,
    ) -> Session:
        """Create a new session"""
        session_id = str(uuid.uuid4())

        session = {
            "id": session_id,
            "user_id": user_id,
            "name": session_data.name or f"Session {datetime.utcnow().strftime('%Y-%m-%d %H:%M')}",
            "llm_provider": session_data.llm_provider,
            "llm_model": session_data.llm_model,
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat(),
        }

        # Store in Redis
        self.redis.hset(f"session:{session_id}", mapping=session)
        self.redis.sadd(f"user:{user_id}:sessions", session_id)

        return Session(
            id=session_id,
            user_id=user_id,
            name=session["name"],
            llm_provider=session_data.llm_provider,
            llm_model=session_data.llm_model,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )

    async def get_session(self, session_id: str) -> Optional[Session]:
        """Get session by ID"""
        session_data = self.redis.hgetall(f"session:{session_id}")
        if not session_data:
            return None

        # Get associated document and draft IDs
        document_ids = list(self.redis.smembers(f"session:{session_id}:documents"))
        draft_ids = list(self.redis.smembers(f"session:{session_id}:drafts"))

        return Session(
            id=session_id,
            user_id=session_data["user_id"],
            name=session_data["name"],
            llm_provider=session_data["llm_provider"],
            llm_model=session_data["llm_model"],
            created_at=datetime.fromisoformat(session_data["created_at"]),
            updated_at=datetime.fromisoformat(session_data["updated_at"]),
            document_ids=document_ids,
            draft_ids=draft_ids,
        )

    async def list_sessions(self, user_id: str) -> List[Session]:
        """List user's sessions"""
        session_ids = self.redis.smembers(f"user:{user_id}:sessions")
        sessions = []

        for session_id in session_ids:
            session = await self.get_session(session_id)
            if session:
                sessions.append(session)

        # Sort by updated_at descending
        sessions.sort(key=lambda x: x.updated_at, reverse=True)
        return sessions

    async def delete_session(self, user_id: str, session_id: str) -> bool:
        """Delete a session"""
        # Verify ownership
        if not self.redis.sismember(f"user:{user_id}:sessions", session_id):
            return False

        # Delete session data
        self.redis.delete(f"session:{session_id}")
        self.redis.delete(f"session:{session_id}:documents")
        self.redis.delete(f"session:{session_id}:drafts")
        self.redis.delete(f"session:{session_id}:chat_history")
        self.redis.srem(f"user:{user_id}:sessions", session_id)

        return True

    async def add_chat_message(
        self,
        session_id: str,
        message: ChatMessage,
    ):
        """Add a message to session chat history"""
        message_data = {
            "role": message.role,
            "content": message.content,
            "timestamp": message.timestamp.isoformat(),
        }

        # Append to chat history list
        self.redis.rpush(
            f"session:{session_id}:chat_history",
            json.dumps(message_data),
        )

        # Update session timestamp
        self.redis.hset(
            f"session:{session_id}",
            "updated_at",
            datetime.utcnow().isoformat(),
        )

    async def get_chat_history(self, session_id: str) -> List[ChatMessage]:
        """Get session chat history"""
        messages = []
        chat_history = self.redis.lrange(f"session:{session_id}:chat_history", 0, -1)

        for message_json in chat_history:
            message_data = json.loads(message_json)
            messages.append(
                ChatMessage(
                    role=message_data["role"],
                    content=message_data["content"],
                    timestamp=datetime.fromisoformat(message_data["timestamp"]),
                )
            )

        return messages


# Global service instance
session_service = SessionService()
