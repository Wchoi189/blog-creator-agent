"""Document processing service"""

import uuid
import os
import shutil
from datetime import datetime
from pathlib import Path
from typing import List, Optional
from fastapi import UploadFile

from backend.core.database import db
from backend.config import settings
from backend.models.documents import (
    Document,
    DocumentType,
    ProcessingStatus,
    DocumentMetadata,
)


class DocumentService:
    """Handles document upload and processing"""

    def __init__(self):
        self.redis = db.redis
        self.upload_dir = Path(settings.UPLOAD_DIR)
        self.upload_dir.mkdir(parents=True, exist_ok=True)

    def _get_document_type(self, filename: str) -> DocumentType:
        """Determine document type from filename"""
        ext = Path(filename).suffix.lower()

        if ext == ".pdf":
            return DocumentType.PDF
        elif ext in [".mp3", ".wav", ".m4a"]:
            return DocumentType.AUDIO
        elif ext in [".png", ".jpg", ".jpeg"]:
            return DocumentType.IMAGE
        elif ext in [".md", ".markdown"]:
            return DocumentType.MARKDOWN
        else:
            raise ValueError(f"Unsupported file type: {ext}")

    async def upload_document(
        self, user_id: str, file: UploadFile
    ) -> Document:
        """Upload and save a document"""
        doc_id = str(uuid.uuid4())

        # Validate file size
        if file.size and file.size > settings.MAX_UPLOAD_SIZE:
            raise ValueError(f"File too large. Max size: {settings.MAX_UPLOAD_SIZE} bytes")

        # Determine document type
        file_type = self._get_document_type(file.filename)

        # Save file
        file_path = self.upload_dir / user_id / doc_id / file.filename
        file_path.parent.mkdir(parents=True, exist_ok=True)

        with open(file_path, "wb") as f:
            shutil.copyfileobj(file.file, f)

        # Create document record
        document = {
            "id": doc_id,
            "user_id": user_id,
            "filename": file.filename,
            "file_type": file_type.value,
            "file_path": str(file_path),
            "size": file.size or os.path.getsize(file_path),
            "status": ProcessingStatus.PENDING.value,
            "created_at": datetime.utcnow().isoformat(),
        }

        # Store in Redis
        self.redis.hset(f"document:{doc_id}", mapping=document)
        self.redis.sadd(f"user:{user_id}:documents", doc_id)

        return Document(
            id=doc_id,
            user_id=user_id,
            filename=file.filename,
            file_type=file_type,
            file_path=str(file_path),
            size=document["size"],
            status=ProcessingStatus.PENDING,
            created_at=datetime.utcnow(),
        )

    async def get_document(self, doc_id: str) -> Optional[Document]:
        """Get document by ID"""
        doc_data = self.redis.hgetall(f"document:{doc_id}")
        if not doc_data:
            return None

        return Document(
            id=doc_id,
            user_id=doc_data["user_id"],
            filename=doc_data["filename"],
            file_type=DocumentType(doc_data["file_type"]),
            file_path=doc_data["file_path"],
            size=int(doc_data["size"]),
            status=ProcessingStatus(doc_data["status"]),
            created_at=datetime.fromisoformat(doc_data["created_at"]),
            processed_at=datetime.fromisoformat(doc_data["processed_at"])
            if doc_data.get("processed_at")
            else None,
            chunk_count=int(doc_data["chunk_count"])
            if doc_data.get("chunk_count")
            else None,
        )

    async def list_documents(self, user_id: str) -> List[Document]:
        """List user's documents"""
        doc_ids = self.redis.smembers(f"user:{user_id}:documents")
        documents = []

        for doc_id in doc_ids:
            doc = await self.get_document(doc_id)
            if doc:
                documents.append(doc)

        # Sort by created_at descending
        documents.sort(key=lambda x: x.created_at, reverse=True)
        return documents

    async def delete_document(self, user_id: str, doc_id: str) -> bool:
        """Delete a document"""
        # Verify ownership
        if not self.redis.sismember(f"user:{user_id}:documents", doc_id):
            return False

        # Get document data
        doc = await self.get_document(doc_id)
        if doc:
            # Delete file
            try:
                Path(doc.file_path).unlink()
                # Try to delete parent directories if empty
                Path(doc.file_path).parent.rmdir()
            except Exception:
                pass  # File might already be deleted

        # Delete from Redis
        self.redis.delete(f"document:{doc_id}")
        self.redis.srem(f"user:{user_id}:documents", doc_id)

        return True

    async def process_document(self, doc_id: str):
        """Process document (extract text and store in Redis)"""
        # Update status
        self.redis.hset(f"document:{doc_id}", "status", ProcessingStatus.PROCESSING.value)

        try:
            doc = await self.get_document(doc_id)
            if not doc:
                raise ValueError("Document not found")

            # Extract text based on document type
            extracted_text = ""
            
            if doc.file_type == DocumentType.MARKDOWN:
                extracted_text = Path(doc.file_path).read_text(encoding="utf-8")
            elif doc.file_type == DocumentType.PDF:
                try:
                    import pypdf
                    with open(doc.file_path, 'rb') as f:
                        reader = pypdf.PdfReader(f)
                        for page in reader.pages:
                            extracted_text += page.extract_text() + "\n\n"
                except ImportError:
                    # Fall back to basic file reading if pypdf not available
                    extracted_text = f"[PDF content from {doc.filename} - pypdf not installed]"
            elif doc.file_type == DocumentType.IMAGE:
                # For images, store a placeholder - OCR would require additional setup
                extracted_text = f"[Image content from {doc.filename}]"
            elif doc.file_type == DocumentType.AUDIO:
                # For audio, store a placeholder - transcription would require additional setup
                extracted_text = f"[Audio content from {doc.filename}]"

            # Store extracted text in Redis (for use in blog generation)
            self.redis.hset(
                f"document:{doc_id}",
                mapping={
                    "status": ProcessingStatus.COMPLETED.value,
                    "processed_at": datetime.utcnow().isoformat(),
                    "chunk_count": str(len(extracted_text.split('\n\n'))),
                    "extracted_text": extracted_text[:50000],  # Limit to 50KB per doc
                },
            )

        except Exception as e:
            # Mark as failed
            self.redis.hset(
                f"document:{doc_id}",
                mapping={
                    "status": ProcessingStatus.FAILED.value,
                    "error_message": str(e),
                },
            )
            raise


# Global service instance
document_service = DocumentService()
