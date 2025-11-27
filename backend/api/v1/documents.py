"""Document API endpoints"""

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, BackgroundTasks
from backend.models.documents import (
    Document,
    DocumentList,
    DocumentSearch,
    SearchResponse,
)
from backend.services.document_service import document_service
from backend.core.security import get_current_user_id

router = APIRouter(prefix="/documents", tags=["Documents"])


@router.post("/upload", response_model=Document, status_code=status.HTTP_201_CREATED)
async def upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    user_id: str = Depends(get_current_user_id),
):
    """Upload a document (PDF, audio, image)"""
    try:
        document = await document_service.upload_document(user_id, file)

        # Process document in background
        background_tasks.add_task(document_service.process_document, document.id)

        return document
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("", response_model=DocumentList)
async def list_documents(user_id: str = Depends(get_current_user_id)):
    """List user's documents"""
    documents = await document_service.list_documents(user_id)
    return DocumentList(documents=documents, total=len(documents))


@router.get("/{doc_id}", response_model=Document)
async def get_document(
    doc_id: str,
    user_id: str = Depends(get_current_user_id),
):
    """Get document details"""
    document = await document_service.get_document(doc_id)

    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found",
        )

    # Verify ownership
    if document.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied",
        )

    return document


@router.delete("/{doc_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_document(
    doc_id: str,
    user_id: str = Depends(get_current_user_id),
):
    """Delete a document"""
    success = await document_service.delete_document(user_id, doc_id)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found",
        )

    return None


@router.post("/{doc_id}/process", response_model=Document)
async def process_document(
    doc_id: str,
    background_tasks: BackgroundTasks,
    user_id: str = Depends(get_current_user_id),
):
    """Manually trigger document processing"""
    document = await document_service.get_document(doc_id)

    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found",
        )

    if document.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied",
        )

    # Process in background
    background_tasks.add_task(document_service.process_document, doc_id)

    return document


@router.post("/search", response_model=SearchResponse)
async def search_documents(
    search_request: DocumentSearch,
    user_id: str = Depends(get_current_user_id),
):
    """Search documents using RAG"""
    results = await document_service.search_document_chunks(
        user_id=user_id,
        query=search_request.query,
        document_ids=search_request.document_ids,
        top_k=search_request.top_k,
    )

    return SearchResponse(results=results, total=len(results))
