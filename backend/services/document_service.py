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
        self.chromadb = db.chromadb
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

            # Delete from ChromaDB collection
            try:
                collection = self.chromadb.get_collection(f"doc_{doc_id}")
                self.chromadb.delete_collection(collection.name)
            except Exception:
                pass  # Collection might not exist

        # Delete from Redis
        self.redis.delete(f"document:{doc_id}")
        self.redis.srem(f"user:{user_id}:documents", doc_id)

        return True

    async def process_document(self, doc_id: str):
        """Process document (extract text, chunk, vectorize)"""
        # Update status
        self.redis.hset(f"document:{doc_id}", "status", ProcessingStatus.PROCESSING.value)

        try:
            doc = await self.get_document(doc_id)
            if not doc:
                raise ValueError("Document not found")

            # Import document preprocessor from existing code
            from src.document_preprocessor import DocumentPreprocessor
            from src.vector_store import VectorStoreFactory
            from src.config import DocumentConfig

            # Initialize preprocessor
            preprocessor = DocumentPreprocessor()

            # Process document based on type
            documents = preprocessor.preprocess([doc.file_path])

            # Create vector store collection for this document
            vector_store = VectorStoreFactory.create_vector_store(
                collection_name=f"doc_{doc_id}",
                persist_directory=settings.CHROMADB_PATH,
            )

            # Add documents to vector store
            vector_store.add_documents(documents)

            # Update document status
            self.redis.hset(
                f"document:{doc_id}",
                mapping={
                    "status": ProcessingStatus.COMPLETED.value,
                    "processed_at": datetime.utcnow().isoformat(),
                    "chunk_count": str(len(documents)),
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
