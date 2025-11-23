"""Blog generation API endpoints"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from typing import List

from backend.models.blog import (
    BlogGenerateRequest,
    BlogRefineRequest,
    BlogDraft,
    BlogDraftUpdate,
    BlogExportRequest,
)
from backend.services.blog_service import blog_service
from backend.core.security import get_current_user_id

router = APIRouter(prefix="/blog", tags=["Blog"])


@router.post("/generate", response_model=BlogDraft, status_code=status.HTTP_201_CREATED)
async def generate_blog(
    request: BlogGenerateRequest,
    session_id: str,
    user_id: str = Depends(get_current_user_id),
):
    """Generate a new blog draft from documents"""
    try:
        draft = await blog_service.create_draft(user_id, session_id, request)
        return draft
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{draft_id}/generate-content")
async def generate_content(
    draft_id: str,
    instructions: str = None,
    user_id: str = Depends(get_current_user_id),
):
    """Generate blog content (streaming response)"""
    draft = await blog_service.get_draft(draft_id)
    if not draft:
        raise HTTPException(status_code=404, detail="Draft not found")

    if draft.user_id != user_id:
        raise HTTPException(status_code=403, detail="Access denied")

    async def generate_stream():
        try:
            async for chunk in blog_service.generate_content(draft_id, instructions):
                yield chunk
        except Exception as e:
            yield f"\n\nError: {str(e)}"

    return StreamingResponse(generate_stream(), media_type="text/plain")


@router.post("/{draft_id}/refine")
async def refine_blog(
    draft_id: str,
    request: BlogRefineRequest,
    user_id: str = Depends(get_current_user_id),
):
    """Refine blog draft with feedback (streaming)"""
    draft = await blog_service.get_draft(draft_id)
    if not draft:
        raise HTTPException(status_code=404, detail="Draft not found")

    if draft.user_id != user_id:
        raise HTTPException(status_code=403, detail="Access denied")

    async def refine_stream():
        try:
            async for chunk in blog_service.refine_content(draft_id, request.feedback):
                yield chunk
        except Exception as e:
            yield f"\n\nError: {str(e)}"

    return StreamingResponse(refine_stream(), media_type="text/plain")


@router.get("", response_model=List[BlogDraft])
async def list_drafts(user_id: str = Depends(get_current_user_id)):
    """List user's blog drafts"""
    drafts = await blog_service.list_drafts(user_id)
    return drafts


@router.get("/{draft_id}", response_model=BlogDraft)
async def get_draft(
    draft_id: str,
    user_id: str = Depends(get_current_user_id),
):
    """Get blog draft by ID"""
    draft = await blog_service.get_draft(draft_id)
    if not draft:
        raise HTTPException(status_code=404, detail="Draft not found")

    if draft.user_id != user_id:
        raise HTTPException(status_code=403, detail="Access denied")

    return draft


@router.put("/{draft_id}", response_model=BlogDraft)
async def update_draft(
    draft_id: str,
    update: BlogDraftUpdate,
    user_id: str = Depends(get_current_user_id),
):
    """Update blog draft"""
    draft = await blog_service.get_draft(draft_id)
    if not draft:
        raise HTTPException(status_code=404, detail="Draft not found")

    if draft.user_id != user_id:
        raise HTTPException(status_code=403, detail="Access denied")

    try:
        updated_draft = await blog_service.update_draft(draft_id, update)
        return updated_draft
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{draft_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_draft(
    draft_id: str,
    user_id: str = Depends(get_current_user_id),
):
    """Delete a blog draft"""
    success = await blog_service.delete_draft(user_id, draft_id)
    if not success:
        raise HTTPException(status_code=404, detail="Draft not found")

    return None


@router.post("/{draft_id}/export")
async def export_draft(
    draft_id: str,
    request: BlogExportRequest,
    user_id: str = Depends(get_current_user_id),
):
    """Export draft to markdown"""
    draft = await blog_service.get_draft(draft_id)
    if not draft:
        raise HTTPException(status_code=404, detail="Draft not found")

    if draft.user_id != user_id:
        raise HTTPException(status_code=403, detail="Access denied")

    # Format as markdown with front matter
    markdown = f"""---
title: {draft.title}
categories: {', '.join(draft.categories)}
tags: {', '.join(draft.tags)}
---

{draft.content}
"""

    return StreamingResponse(
        iter([markdown]),
        media_type="text/markdown",
        headers={
            "Content-Disposition": f"attachment; filename={draft.title.lower().replace(' ', '-')}.md"
        },
    )
