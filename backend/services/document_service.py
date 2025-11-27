"""Document processing service with RAG indexing support"""

import logging
import os
import shutil
import uuid
from datetime import datetime
from pathlib import Path
from typing import List, Optional

from fastapi import UploadFile
from langchain_core.documents import Document as LCDocument
from langchain_text_splitters import RecursiveCharacterTextSplitter

from backend.config import settings
from backend.core.database import db
from backend.models.documents import (
    Document,
    DocumentType,
    ProcessingStatus,
    SearchResult,
)


logger = logging.getLogger(__name__)


class DocumentService:
    """Handles document upload and processing"""

    def __init__(self):
        self.redis = db.redis
        self.elasticsearch = db.elasticsearch
        self.upload_dir = Path(settings.UPLOAD_DIR)
        self.upload_dir.mkdir(parents=True, exist_ok=True)
        self._es_index = "documents"
        self._es_index_ready = False

    def _get_document_type(self, filename: str) -> DocumentType:
        """Determine document type from filename"""
        ext = Path(filename).suffix.lower()

        if ext == ".pdf":
            return DocumentType.PDF
        if ext in [".mp3", ".wav", ".m4a"]:
            return DocumentType.AUDIO
        if ext in [".png", ".jpg", ".jpeg"]:
            return DocumentType.IMAGE
        if ext in [".md", ".markdown"]:
            return DocumentType.MARKDOWN
        if ext == ".txt":
            return DocumentType.TEXT
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

        # Delete from Redis and search index
        self.redis.delete(f"document:{doc_id}")
        self.redis.delete(f"document:{doc_id}:content")
        self.redis.srem(f"user:{user_id}:documents", doc_id)

        await self._delete_indexed_chunks(doc_id)

        return True

    async def process_document(self, doc_id: str):
        """Process document (extract, chunk, index)"""
        # Update status
        self.redis.hset(f"document:{doc_id}", "status", ProcessingStatus.PROCESSING.value)

        try:
            doc = await self.get_document(doc_id)
            if not doc:
                raise ValueError("Document not found")

            chunks = await self._extract_and_chunk(doc)

            # Store chunk content for quick retrieval
            self.redis.delete(f"document:{doc_id}:content")
            chunk_texts = []
            for i, chunk in enumerate(chunks):
                content = (chunk.page_content or "").strip()
                if not content:
                    continue
                chunk_texts.append(content)
                self.redis.hset(
                    f"document:{doc_id}:content",
                    f"chunk_{i}",
                    content,
                )

            extracted_text = "\n\n".join(chunk_texts)
            chunk_count = len(chunk_texts)

            # Update metadata on the document itself
            self.redis.hset(
                f"document:{doc_id}",
                mapping={
                    "status": ProcessingStatus.COMPLETED.value,
                    "processed_at": datetime.utcnow().isoformat(),
                    "chunk_count": str(chunk_count),
                    "extracted_text": extracted_text[:50000],
                },
            )

            # Index chunks for ElasticSearch-backed retrieval
            if chunk_texts:
                await self._index_chunks(doc, chunk_texts)

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

    async def search_document_chunks(
        self,
        user_id: str,
        query: str,
        document_ids: Optional[List[str]] = None,
        top_k: int = settings.TOP_K_RESULTS,
    ) -> List[SearchResult]:
        """Search processed document chunks for RAG."""

        user_documents = self.redis.smembers(f"user:{user_id}:documents")
        if not user_documents:
            return []

        allowed_docs = list(user_documents)
        if document_ids:
            allowed_docs = [doc_id for doc_id in document_ids if doc_id in user_documents]
            if not allowed_docs:
                return []

        if self.elasticsearch:
            results = await self._search_with_elasticsearch(
                query=query,
                user_id=user_id,
                document_ids=allowed_docs,
                top_k=top_k,
            )
            if results:
                return results

        # Fallback to Redis-based keyword search
        return await self._fallback_search(query, allowed_docs, top_k)


    async def get_document_content(self, doc_id: str) -> str:
        """Get full document content from Redis."""
        content_data = self.redis.hgetall(f"document:{doc_id}:content")
        if not content_data:
            return ""

        chunks = sorted(
            content_data.items(),
            key=lambda item: int(item[0].split("_")[1]),
        )
        return "\n\n".join(chunk for _, chunk in chunks)

    async def _extract_and_chunk(self, doc: Document) -> List[LCDocument]:
        path = Path(doc.file_path)

        if doc.file_type == DocumentType.MARKDOWN:
            return self._split_text(path.read_text(encoding="utf-8"), path)
        if doc.file_type == DocumentType.TEXT:
            return self._split_text(path.read_text(encoding="utf-8"), path)
        if doc.file_type == DocumentType.PDF:
            return await self._process_pdf(path)
        if doc.file_type == DocumentType.AUDIO:
            return [self._placeholder_chunk(doc.filename, "audio")]
        if doc.file_type == DocumentType.IMAGE:
            return [self._placeholder_chunk(doc.filename, "image")]

        raise ValueError(f"Processing not implemented for {doc.file_type}")

    def _split_text(self, text: str, path: Path) -> List[LCDocument]:
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=settings.CHUNK_SIZE,
            chunk_overlap=settings.CHUNK_OVERLAP,
        )
        base_doc = LCDocument(page_content=text, metadata={"source": str(path)})
        return splitter.split_documents([base_doc])

    async def _process_pdf(self, path: Path) -> List[LCDocument]:
        try:
            try:
                import fitz  # type: ignore
            except ImportError:
                import pymupdf as fitz  # type: ignore

            doc = fitz.open(str(path))
            text = "".join(page.get_text() for page in doc)
            doc.close()
            return self._split_text(text, path)
        except ImportError as exc:
            raise ValueError("PyMuPDF not installed for PDF processing") from exc

    def _placeholder_chunk(self, filename: str, kind: str) -> LCDocument:
        message = f"[{kind.capitalize()} content from {filename}]"
        return LCDocument(page_content=message, metadata={"source": filename})

    async def _index_chunks(self, doc: Document, chunks: List[str]):
        if not self.elasticsearch:
            return
        await self._ensure_index()
        for idx, content in enumerate(chunks):
            body = {
                "document_id": doc.id,
                "document_name": doc.filename,
                "user_id": doc.user_id,
                "chunk_index": idx,
                "content": content,
                "created_at": datetime.utcnow().isoformat(),
            }
            try:
                await self.elasticsearch.index(
                    index=self._es_index,
                    id=f"{doc.id}_{idx}",
                    document=body,
                    refresh="wait_for",
                )
            except Exception as exc:
                logger.warning("Failed to index chunk %s_%s: %s", doc.id, idx, exc)
                break

    async def _ensure_index(self):
        if not self.elasticsearch or self._es_index_ready:
            return
        try:
            exists = await self.elasticsearch.indices.exists(index=self._es_index)
            if not exists:
                await self.elasticsearch.indices.create(
                    index=self._es_index,
                    mappings={
                        "properties": {
                            "document_id": {"type": "keyword"},
                            "document_name": {"type": "keyword"},
                            "user_id": {"type": "keyword"},
                            "chunk_index": {"type": "integer"},
                            "content": {"type": "text"},
                            "created_at": {"type": "date"},
                        }
                    },
                )
            self._es_index_ready = True
        except Exception as exc:
            logger.warning("Unable to ensure ElasticSearch index: %s", exc)

    async def _delete_indexed_chunks(self, doc_id: str):
        if not self.elasticsearch:
            return
        await self._ensure_index()
        try:
            await self.elasticsearch.delete_by_query(
                index=self._es_index,
                query={"term": {"document_id": doc_id}},
                conflicts="proceed",
            )
        except Exception as exc:
            logger.warning("Failed to delete indexed chunks for %s: %s", doc_id, exc)

    async def _search_with_elasticsearch(
        self,
        *,
        query: str,
        user_id: str,
        document_ids: List[str],
        top_k: int,
    ) -> List[SearchResult]:
        if not self.elasticsearch:
            return []
        await self._ensure_index()
        user_query = query.strip() or "relevant context"
        try:
            response = await self.elasticsearch.search(
                index=self._es_index,
                size=top_k,
                query={
                    "bool": {
                        "must": [
                            {
                                "multi_match": {
                                    "query": user_query,
                                    "fields": ["content^3", "document_name"],
                                }
                            }
                        ],
                        "filter": [
                            {"term": {"user_id": user_id}},
                            {"terms": {"document_id": document_ids}},
                        ],
                    }
                },
            )
        except Exception as exc:
            logger.warning("ElasticSearch query failed: %s", exc)
            return []

        hits = response.get("hits", {}).get("hits", [])
        results: List[SearchResult] = []
        for hit in hits:
            source = hit.get("_source", {})
            results.append(
                SearchResult(
                    content=source.get("content", ""),
                    document_id=source.get("document_id", ""),
                    document_name=source.get("document_name", "unknown"),
                    score=float(hit.get("_score", 0.0)),
                    metadata={"chunk_index": source.get("chunk_index")},
                )
            )
        return results

    async def _fallback_search(
        self,
        query: str,
        document_ids: List[str],
        top_k: int,
    ) -> List[SearchResult]:
        lowered_query = query.lower().strip()
        results: List[SearchResult] = []

        for doc_id in document_ids:
            doc_meta = self.redis.hgetall(f"document:{doc_id}")
            chunks = self.redis.hgetall(f"document:{doc_id}:content")
            for chunk_key, content in chunks.items():
                if not content:
                    continue
                score = (
                    content.lower().count(lowered_query)
                    if lowered_query
                    else len(content)
                )
                if score <= 0:
                    continue
                results.append(
                    SearchResult(
                        content=content,
                        document_id=doc_id,
                        document_name=doc_meta.get("filename", doc_id),
                        score=float(score),
                        metadata={"chunk_key": chunk_key},
                    )
                )

        results.sort(key=lambda item: item.score, reverse=True)
        return results[:top_k]


# Global service instance
document_service = DocumentService()
