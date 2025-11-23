#!/usr/bin/env python3
"""
Setup script for AI Agent Semantic Search Tool

This script helps set up the semantic search functionality for AI agents
by indexing the codebase and making it searchable.
"""

import argparse
import logging
import sys

from AgentQMS.agent_tools.utils.runtime import ensure_project_root_on_sys_path

ensure_project_root_on_sys_path()

from agent.tools.semantic_search.agent_semantic_search import AgentSemanticSearch

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main():
    parser = argparse.ArgumentParser(description="Setup AI Agent Semantic Search")
    parser.add_argument(
        "--index", action="store_true", help="Index the codebase for semantic search"
    )
    parser.add_argument(
        "--test", action="store_true", help="Test the search functionality"
    )
    parser.add_argument("--query", type=str, help="Test query to run")
    parser.add_argument(
        "--es-host",
        type=str,
        default="http://host.docker.internal:9201",
        help="Elasticsearch host URL",
    )
    parser.add_argument(
        "--index-name",
        type=str,
        default="agent_codebase",
        help="Elasticsearch index name",
    )

    args = parser.parse_args()

    try:
        # Initialize search tool
        search = AgentSemanticSearch(es_host=args.es_host, index_name=args.index_name)
        logger.info("✅ Connected to Elasticsearch")

        if args.index:
            logger.info("🔄 Starting codebase indexing...")
            # Index the project (excluding data, logs, etc.)
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
            ]
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
                "**/logs/**",
                "**/output/**",
                "**/results/**",
            ]

            indexed_count = search.index_codebase(
                include_patterns=include_patterns, exclude_patterns=exclude_patterns
            )
            logger.info(f"✅ Indexed {indexed_count} documents")

        if args.test or args.query:
            if args.query:
                logger.info(f"🔍 Testing search with query: {args.query}")
                results = search.semantic_search(args.query, top_k=5)
            else:
                # Default test queries
                test_queries = [
                    "Korean grammar correction",
                    "semantic search",
                    "training data",
                ]

                for query in test_queries:
                    logger.info(f"🔍 Testing query: {query}")
                    results = search.semantic_search(query, top_k=3)

                    if results:
                        for result in results:
                            print(
                                f"  📄 {result.file_path} (score: {result.score:.3f})"
                            )
                            print(f"     {result.content[:100]}...")
                    else:
                        print("     No results found")
                    print()

        if not args.index and not args.test and not args.query:
            parser.print_help()

    except Exception as e:
        logger.error(f"❌ Setup failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
