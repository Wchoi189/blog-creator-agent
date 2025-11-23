#!/usr/bin/env python3
"""
AI Agent Semantic Search Tool

Provides AI agents with semantic search capabilities across the codebase,
documentation, and training data using Elasticsearch for Korean language support.
"""

import logging
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from elasticsearch import Elasticsearch

logger = logging.getLogger(__name__)


@dataclass
class SearchResult:
    """Search result with metadata."""

    content: str
    file_path: str
    line_number: int | None
    score: float
    content_type: str  # 'code', 'documentation', 'training_data', etc.
    metadata: dict[str, Any]


class AgentSemanticSearch:
    """
    Semantic search tool for AI agents.

    Provides unified search across:
    - Source code and documentation
    - Training data and examples
    - Research and analysis artifacts
    - Korean language content with proper analysis
    """

    def __init__(self, es_host: str = None, index_name: str = "agent_codebase"):
        """
        Initialize the agent semantic search tool.

        Args:
            es_host: Elasticsearch host URL
            index_name: Name of the search index
        """
        self.index_name = index_name

        if es_host is None:
            es_host = os.getenv("ELASTICSEARCH_URL", "http://localhost:9200")

        self.es = Elasticsearch([es_host])

        # Test connection
        try:
            info = self.es.info()
            logger.info(f"Connected to Elasticsearch: {info['cluster_name']}")
        except Exception as e:
            logger.error(f"Cannot connect to Elasticsearch: {e}")
            raise

        # Create index if needed
        self._ensure_index()

    def _ensure_index(self):
        """Create index with Korean language support."""
        if not self.es.indices.exists(index=self.index_name):
            # Use Nori analyzer for Korean, fallback to CJK, then standard
            index_settings = {
                "settings": {
                    "analysis": {
                        "analyzer": {
                            "korean_analyzer": {
                                "type": "custom",
                                "tokenizer": "nori_tokenizer",
                                "filter": ["nori_part_of_speech"],
                            }
                        }
                    }
                },
                "mappings": {
                    "properties": {
                        "content": {
                            "type": "text",
                            "analyzer": "korean_analyzer",
                            "fields": {
                                "keyword": {"type": "keyword", "ignore_above": 256}
                            },
                        },
                        "file_path": {"type": "keyword"},
                        "line_number": {"type": "integer"},
                        "content_type": {"type": "keyword"},
                        "language": {"type": "keyword"},
                        "metadata": {"type": "object"},
                        "embedding": {
                            "type": "dense_vector",
                            "dims": 768,
                            "index": True,
                            "similarity": "cosine",
                        },
                    }
                },
            }

            try:
                self.es.indices.create(index=self.index_name, body=index_settings)
                logger.info(f"Created index: {self.index_name}")
            except Exception as e:
                logger.warning(f"Failed to create index with Korean analyzer: {e}")
                # Fallback to standard analyzer
                fallback_settings = {
                    "mappings": {
                        "properties": {
                            "content": {"type": "text"},
                            "file_path": {"type": "keyword"},
                            "line_number": {"type": "integer"},
                            "content_type": {"type": "keyword"},
                            "language": {"type": "keyword"},
                            "metadata": {"type": "object"},
                        }
                    }
                }
                self.es.indices.create(index=self.index_name, body=fallback_settings)
                logger.info(f"Created index with standard analyzer: {self.index_name}")

    def index_codebase(
        self,
        root_path: str = None,
        include_patterns: list[str] = None,
        exclude_patterns: list[str] = None,
    ) -> int:
        """
        Index the entire codebase for semantic search.

        Args:
            root_path: Root directory to index (defaults to project root)
            include_patterns: File patterns to include
            exclude_patterns: File patterns to exclude

        Returns:
            Number of documents indexed
        """
        if root_path is None:
            root_path = Path(
                __file__
            ).parent.parent.parent.parent  # Go up to project root

        root_path = Path(root_path)

        if include_patterns is None:
            include_patterns = [
                "**/*.py",
                "**/*.md",
                "**/*.txt",
                "**/*.json",
                "**/*.yaml",
                "**/*.yml",
                "**/*.sh",
                "**/*.bash",
                "**/*.sql",
                "**/*.csv",
            ]

        if exclude_patterns is None:
            exclude_patterns = [
                "**/.git/**",
                "**/__pycache__/**",
                "**/node_modules/**",
                "**/.venv/**",
                "**/build/**",
                "**/dist/**",
                "**/*.log",
                "**/htmlcov/**",
                "**/.mypy_cache/**",
                "**/data/**",
            ]

        documents = []
        indexed_count = 0

        for pattern in include_patterns:
            for file_path in root_path.glob(pattern):
                if file_path.is_file():
                    # Check exclude patterns
                    should_exclude = False
                    for exclude_pattern in exclude_patterns:
                        if file_path.match(exclude_pattern):
                            should_exclude = True
                            break

                    if not should_exclude:
                        try:
                            docs = self._index_file(file_path)
                            documents.extend(docs)
                            indexed_count += len(docs)
                        except Exception as e:
                            logger.warning(f"Failed to index {file_path}: {e}")

        # Bulk index documents
        if documents:
            self._bulk_index(documents)

        logger.info(f"Indexed {indexed_count} documents from codebase")
        return indexed_count

    def _index_file(self, file_path: Path) -> list[dict[str, Any]]:
        """Index a single file, splitting into searchable chunks."""
        documents = []

        try:
            with open(file_path, encoding="utf-8") as f:
                content = f.read()
        except UnicodeDecodeError:
            # Skip binary files
            return documents

        # Determine content type and language
        suffix = file_path.suffix.lower()
        if suffix == ".py":
            content_type = "code"
            language = "python"
        elif suffix == ".md":
            content_type = "documentation"
            language = "markdown"
        elif suffix in [".json", ".yaml", ".yml"]:
            content_type = "configuration"
            language = "json"
        elif suffix == ".sh":
            content_type = "script"
            language = "bash"
        else:
            content_type = "text"
            language = "unknown"

        # Split content into chunks (by lines for code, paragraphs for docs)
        if content_type == "code":
            lines = content.split("\n")
            chunk_size = 20  # Lines per chunk
            for i in range(0, len(lines), chunk_size):
                chunk_lines = lines[i : i + chunk_size]
                chunk_content = "\n".join(chunk_lines)

                if chunk_content.strip():  # Skip empty chunks
                    doc = {
                        "content": chunk_content,
                        "file_path": str(file_path),
                        "line_number": i + 1,
                        "content_type": content_type,
                        "language": language,
                        "metadata": {
                            "file_size": len(content),
                            "chunk_start": i + 1,
                            "chunk_end": min(i + chunk_size, len(lines)),
                        },
                    }
                    documents.append(doc)
        else:
            # For documentation and other text, split by paragraphs
            paragraphs = [p.strip() for p in content.split("\n\n") if p.strip()]

            for i, paragraph in enumerate(paragraphs):
                if len(paragraph) > 50:  # Skip very short paragraphs
                    doc = {
                        "content": paragraph,
                        "file_path": str(file_path),
                        "line_number": None,  # Not applicable for paragraph-based chunking
                        "content_type": content_type,
                        "language": language,
                        "metadata": {"file_size": len(content), "paragraph_index": i},
                    }
                    documents.append(doc)

        return documents

    def _bulk_index(self, documents: list[dict[str, Any]]) -> int:
        """Bulk index documents into Elasticsearch."""
        if not documents:
            return 0

        def generate_actions():
            for doc in documents:
                yield {"_index": self.index_name, "_source": doc}

        try:
            from elasticsearch.helpers import bulk

            success, failed = bulk(self.es, generate_actions(), raise_on_error=False)

            if failed:
                logger.warning(f"Failed to index {len(failed)} documents")

            logger.info(f"Successfully indexed {success} documents")
            return success

        except Exception as e:
            logger.error(f"Bulk indexing failed: {e}")
            return 0

    def semantic_search(
        self,
        query: str,
        content_types: list[str] = None,
        top_k: int = 10,
        min_score: float = 0.1,
    ) -> list[SearchResult]:
        """
        Perform semantic search across the indexed codebase.

        Args:
            query: Natural language search query
            content_types: Filter by content types ('code', 'documentation', etc.)
            top_k: Number of results to return
            min_score: Minimum relevance score

        Returns:
            List of search results with metadata
        """
        # Build search query
        search_body = {
            "size": top_k,
            "query": {
                "bool": {
                    "must": [
                        {
                            "multi_match": {
                                "query": query,
                                "fields": ["content"],
                                "fuzziness": "AUTO",
                            }
                        }
                    ],
                    "filter": [],
                }
            },
            "sort": ["_score"],
            "min_score": min_score,
        }

        # Add content type filter
        if content_types:
            search_body["query"]["bool"]["filter"].append(
                {"terms": {"content_type": content_types}}
            )

        try:
            response = self.es.search(index=self.index_name, body=search_body)

            results = []
            for hit in response["hits"]["hits"]:
                source = hit["_source"]
                result = SearchResult(
                    content=source["content"],
                    file_path=source["file_path"],
                    line_number=source.get("line_number"),
                    score=hit["_score"],
                    content_type=source["content_type"],
                    metadata=source.get("metadata", {}),
                )
                results.append(result)

            logger.info(f"Found {len(results)} results for query: {query[:50]}...")
            return results

        except Exception as e:
            logger.error(f"Search failed: {e}")
            return []

    def search_code(
        self, query: str, language: str = None, top_k: int = 10
    ) -> list[SearchResult]:
        """Search specifically for code snippets."""
        content_types = ["code"]
        if language:
            # Would need to add language filtering in the query
            pass
        return self.semantic_search(query, content_types, top_k)

    def search_documentation(self, query: str, top_k: int = 10) -> list[SearchResult]:
        """Search specifically for documentation."""
        return self.semantic_search(query, ["documentation"], top_k)

    def find_similar_code(
        self, code_snippet: str, top_k: int = 5
    ) -> list[SearchResult]:
        """Find code similar to the provided snippet."""
        return self.search_code(code_snippet, top_k=top_k)

    def explain_concept(self, concept: str, top_k: int = 3) -> list[SearchResult]:
        """Find explanations or documentation about a concept."""
        return self.search_documentation(concept, top_k=top_k)


# Convenience functions for AI agents
def search_codebase(query: str, content_type: str = None) -> str:
    """
    AI agent convenience function for searching the codebase.

    Args:
        query: What to search for
        content_type: 'code', 'documentation', or None for all

    Returns:
        Formatted search results
    """
    try:
        search = AgentSemanticSearch()

        if content_type == "code":
            results = search.search_code(query)
        elif content_type == "documentation":
            results = search.search_documentation(query)
        else:
            results = search.semantic_search(query)

        if not results:
            return f"No results found for: {query}"

        output = f"Search results for '{query}':\n\n"
        for i, result in enumerate(results, 1):
            output += f"{i}. **{result.file_path}**"
            if result.line_number:
                output += f" (line {result.line_number})"
            output += f" - Score: {result.score:.3f}\n"
            output += f"   Type: {result.content_type}\n"
            output += f"   Content: {result.content[:200]}{'...' if len(result.content) > 200 else ''}\n\n"

        return output

    except Exception as e:
        return f"Search failed: {e}"


if __name__ == "__main__":
    # Example usage for testing
    search = AgentSemanticSearch()

    # Index the codebase (run once)
    # search.index_codebase()

    # Search examples
    results = search.semantic_search("Korean grammar correction")
    for result in results[:3]:
        print(f"File: {result.file_path}")
        print(f"Content: {result.content[:100]}...")
        print(f"Score: {result.score:.3f}")
        print("---")
