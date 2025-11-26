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
        """Generate blog content using LangGraph agent (streaming)"""
        draft = await self.get_draft(draft_id)
        if not draft:
            raise ValueError("Draft not found")

        # Update status
        self.redis.hset(f"draft:{draft_id}", "status", BlogStatus.GENERATING.value)

        try:
            # Import agent from existing code
            from src.agent import BlogContentAgent
            from src.retriever import RetrieverFactory
            from src.vector_store import VectorStoreFactory

            # Create retrievers for each document
            retrievers = []
            for doc_id in draft.document_ids:
                vector_store = VectorStoreFactory.create_vector_store(
                    collection_name=f"doc_{doc_id}",
                    persist_directory=settings.CHROMADB_PATH,
                )
                retriever = vector_store.as_retriever(search_kwargs={"k": settings.TOP_K_RESULTS})
                retrievers.append(retriever)

            # Combine retrievers (use first for now, can merge later)
            retriever = retrievers[0] if retrievers else None

            if not retriever:
                raise ValueError("No documents available for generation")

            # Create agent
            agent = BlogContentAgent(
                retriever=retriever,
                documents=[],  # Documents already in vector store
                llm_provider=settings.DEFAULT_LLM_PROVIDER,
                llm_model=settings.DEFAULT_LLM_MODEL,
                agent_profile="draft",
            )

            # Generate content with streaming
            session_id = draft.session_id
            prompt = instructions or f"Generate a blog post titled '{draft.title}'"

            # Stream response
            full_content = ""
            async for chunk in agent.stream_response(session_id, prompt):
                full_content += chunk
                yield chunk

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

        # Similar to generate_content but with refinement prompt
        async for chunk in self.generate_content(draft_id, feedback):
            yield chunk

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
