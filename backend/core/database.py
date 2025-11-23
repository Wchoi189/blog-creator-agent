"""Database connections and utilities"""

import asyncio
from typing import Optional
from redis import Redis
from elasticsearch import Elasticsearch, AsyncElasticsearch
import chromadb
from chromadb.config import Settings as ChromaSettings

from backend.config import settings


class DatabaseManager:
    """Manages database connections"""

    def __init__(self):
        self._redis: Optional[Redis] = None
        self._elasticsearch: Optional[AsyncElasticsearch] = None
        self._chromadb: Optional[chromadb.Client] = None

    @property
    def redis(self) -> Redis:
        """Get Redis client"""
        if self._redis is None:
            self._redis = Redis.from_url(
                settings.REDIS_URL,
                decode_responses=True,
            )
        return self._redis

    @property
    def elasticsearch(self) -> Optional[AsyncElasticsearch]:
        """Get Elasticsearch client (optional)"""
        if self._elasticsearch is None and settings.ELASTICSEARCH_URL:
            try:
                self._elasticsearch = AsyncElasticsearch(
                    [settings.ELASTICSEARCH_URL],
                    verify_certs=False,
                )
            except Exception as e:
                print(f"⚠️  ElasticSearch unavailable: {e}")
                print("📦 Falling back to ChromaDB only")
                return None
        return self._elasticsearch

    @property
    def chromadb(self) -> chromadb.Client:
        """Get ChromaDB client"""
        if self._chromadb is None:
            self._chromadb = chromadb.Client(
                ChromaSettings(
                    persist_directory=settings.CHROMADB_PATH,
                    anonymized_telemetry=False,
                )
            )
        return self._chromadb

    async def check_health(self) -> dict:
        """Check health of all database connections"""
        health = {}

        # Redis
        try:
            self.redis.ping()
            health["redis"] = "healthy"
        except Exception as e:
            health["redis"] = f"unhealthy: {str(e)}"

        # ElasticSearch (optional)
        if self.elasticsearch:
            try:
                await self.elasticsearch.ping()
                health["elasticsearch"] = "healthy"
            except Exception as e:
                health["elasticsearch"] = f"unhealthy: {str(e)}"
        else:
            health["elasticsearch"] = "not configured"

        # ChromaDB
        try:
            self.chromadb.heartbeat()
            health["chromadb"] = "healthy"
        except Exception as e:
            health["chromadb"] = f"unhealthy: {str(e)}"

        return health

    def close(self):
        """Close all database connections"""
        if self._redis:
            self._redis.close()
        if self._elasticsearch:
            asyncio.create_task(self._elasticsearch.close())


# Global database manager instance
db = DatabaseManager()


# Dependency for FastAPI routes
async def get_db():
    """Dependency to get database manager"""
    return db
