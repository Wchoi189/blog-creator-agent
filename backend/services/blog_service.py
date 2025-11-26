"""Blog generation service"""

import uuid
from datetime import datetime
from typing import Optional, List, AsyncIterator
from backend.core.database import db
from backend.config import settings
from backend.models.blog import (
    BlogDraft,
    BlogStatus,
    BlogGenerateRequest,
    BlogRefineRequest,
    BlogDraftUpdate,
)


class BlogService:
    """Handles blog generation and management"""

    def __init__(self):
        self.redis = db.redis

    async def create_draft(
        self,
        user_id: str,
        session_id: str,
        request: BlogGenerateRequest,
    ) -> BlogDraft:
        """Create a new blog draft"""
        draft_id = str(uuid.uuid4())

        draft = {
            "id": draft_id,
            "user_id": user_id,
            "session_id": session_id,
            "title": request.title or "Untitled Draft",
            "content": "",
            "status": BlogStatus.DRAFT.value,
            "version": "1",
            "document_ids": ",".join(request.document_ids),
            "categories": ",".join(request.categories),
            "tags": ",".join(request.tags),
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat(),
        }

        # Store in Redis
        self.redis.hset(f"draft:{draft_id}", mapping=draft)
        self.redis.sadd(f"user:{user_id}:drafts", draft_id)
        self.redis.sadd(f"session:{session_id}:drafts", draft_id)

        return BlogDraft(
            id=draft_id,
            user_id=user_id,
            session_id=session_id,
            title=draft["title"],
            content="",
            status=BlogStatus.DRAFT,
            version=1,
            document_ids=request.document_ids,
            categories=request.categories,
            tags=request.tags,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )

    async def get_draft(self, draft_id: str) -> Optional[BlogDraft]:
        """Get draft by ID"""
        draft_data = self.redis.hgetall(f"draft:{draft_id}")
        if not draft_data:
            return None

        return BlogDraft(
            id=draft_id,
            user_id=draft_data["user_id"],
            session_id=draft_data["session_id"],
            title=draft_data["title"],
            content=draft_data.get("content", ""),
            status=BlogStatus(draft_data["status"]),
            version=int(draft_data.get("version", "1")),
            document_ids=draft_data.get("document_ids", "").split(",")
            if draft_data.get("document_ids")
            else [],
            categories=draft_data.get("categories", "").split(",")
            if draft_data.get("categories")
            else [],
            tags=draft_data.get("tags", "").split(",")
            if draft_data.get("tags")
            else [],
            created_at=datetime.fromisoformat(draft_data["created_at"]),
            updated_at=datetime.fromisoformat(draft_data["updated_at"]),
            published_at=datetime.fromisoformat(draft_data["published_at"])
            if draft_data.get("published_at")
            else None,
            published_url=draft_data.get("published_url"),
        )

    async def update_draft(
        self,
        draft_id: str,
        update: BlogDraftUpdate,
    ) -> BlogDraft:
        """Update draft content"""
        draft = await self.get_draft(draft_id)
        if not draft:
            raise ValueError("Draft not found")

        # Prepare updates
        updates = {"updated_at": datetime.utcnow().isoformat()}

        if update.title is not None:
            updates["title"] = update.title
        if update.content is not None:
            updates["content"] = update.content
        if update.categories is not None:
            updates["categories"] = ",".join(update.categories)
        if update.tags is not None:
            updates["tags"] = ",".join(update.tags)

        # Update in Redis
        self.redis.hset(f"draft:{draft_id}", mapping=updates)

        # Return updated draft
        return await self.get_draft(draft_id)

    async def generate_content(
        self,
        draft_id: str,
        instructions: Optional[str] = None,
    ) -> AsyncIterator[str]:
        """Generate blog content using LLM (streaming)"""
        draft = await self.get_draft(draft_id)
        if not draft:
            raise ValueError("Draft not found")

        # Update status
        self.redis.hset(f"draft:{draft_id}", "status", BlogStatus.GENERATING.value)

        try:
            from langchain_openai import ChatOpenAI
            from langchain_core.messages import HumanMessage, SystemMessage
            
            # Initialize LLM with streaming
            llm = ChatOpenAI(
                model=settings.DEFAULT_LLM_MODEL,
                temperature=0.7,
                streaming=True,
                api_key=settings.OPENAI_API_KEY,
            )
            
            # Build prompt
            system_prompt = """You are an expert blog content writer. Generate well-structured, 
engaging blog content based on the user's instructions. Use markdown formatting with proper 
headings, paragraphs, and bullet points where appropriate."""
            
            user_prompt = instructions or f"Generate a blog post titled '{draft.title}'"
            if draft.content:
                user_prompt = f"Current content:\n{draft.content}\n\nInstructions: {user_prompt}"
            
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=user_prompt),
            ]
            
            # Stream response
            full_content = ""
            async for chunk in llm.astream(messages):
                if chunk.content:
                    full_content += chunk.content
                    yield chunk.content

            # Update draft with generated content
            await self.update_draft(
                draft_id,
                BlogDraftUpdate(content=full_content),
            )

            # Update status
            self.redis.hset(f"draft:{draft_id}", "status", BlogStatus.COMPLETED.value)

        except Exception as e:
            # Mark as failed
            self.redis.hset(f"draft:{draft_id}", "status", BlogStatus.FAILED.value)
            raise

    async def refine_content(
        self,
        draft_id: str,
        feedback: str,
    ) -> AsyncIterator[str]:
        """Refine blog content based on feedback (streaming)"""
        draft = await self.get_draft(draft_id)
        if not draft:
            raise ValueError("Draft not found")

        # Update status
        self.redis.hset(f"draft:{draft_id}", "status", BlogStatus.GENERATING.value)

        try:
            from langchain_openai import ChatOpenAI
            from langchain_core.messages import HumanMessage, SystemMessage
            
            # Initialize LLM with streaming
            llm = ChatOpenAI(
                model=settings.DEFAULT_LLM_MODEL,
                temperature=0.7,
                streaming=True,
                api_key=settings.OPENAI_API_KEY,
            )
            
            # Build refinement prompt
            system_prompt = """You are an expert blog editor. Your task is to refine and improve 
the provided blog content based on the user's feedback. Maintain the overall structure while 
making the requested improvements. Output the complete refined content in markdown format."""
            
            user_prompt = f"""Current blog content:
{draft.content}

User feedback/instructions:
{feedback}

Please provide the complete refined blog content based on the feedback above."""
            
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=user_prompt),
            ]
            
            # Stream response
            full_content = ""
            async for chunk in llm.astream(messages):
                if chunk.content:
                    full_content += chunk.content
                    yield chunk.content

            # Update draft with refined content
            await self.update_draft(
                draft_id,
                BlogDraftUpdate(content=full_content),
            )

            # Update status
            self.redis.hset(f"draft:{draft_id}", "status", BlogStatus.COMPLETED.value)

        except Exception as e:
            # Mark as failed
            self.redis.hset(f"draft:{draft_id}", "status", BlogStatus.FAILED.value)
            raise

    async def list_drafts(self, user_id: str) -> List[BlogDraft]:
        """List user's drafts"""
        draft_ids = self.redis.smembers(f"user:{user_id}:drafts")
        drafts = []

        for draft_id in draft_ids:
            draft = await self.get_draft(draft_id)
            if draft:
                drafts.append(draft)

        # Sort by updated_at descending
        drafts.sort(key=lambda x: x.updated_at, reverse=True)
        return drafts

    async def delete_draft(self, user_id: str, draft_id: str) -> bool:
        """Delete a draft"""
        # Verify ownership
        if not self.redis.sismember(f"user:{user_id}:drafts", draft_id):
            return False

        draft = await self.get_draft(draft_id)
        if draft:
            # Remove from session
            self.redis.srem(f"session:{draft.session_id}:drafts", draft_id)

        # Delete from Redis
        self.redis.delete(f"draft:{draft_id}")
        self.redis.srem(f"user:{user_id}:drafts", draft_id)

        return True


# Global service instance
blog_service = BlogService()
