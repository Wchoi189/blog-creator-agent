#!/usr/bin/env python3
"""
Test script for AI Agent Semantic Search Tool
"""

import sys

import pytest

from AgentQMS.agent_tools.utils.runtime import ensure_project_root_on_sys_path

ensure_project_root_on_sys_path()

semantic_module = pytest.importorskip(
    "agent.tools.semantic_search.agent_semantic_search",
    reason="Semantic search module not bundled with core AgentQMS artifacts.",
)

AgentSemanticSearch = getattr(semantic_module, "AgentSemanticSearch", None)
search_codebase = getattr(semantic_module, "search_codebase", None)


def test_import():
    """Test that the module can be imported."""
    assert AgentSemanticSearch is not None
    assert search_codebase is not None


def test_connection():
    """Test Elasticsearch connection."""
    try:
        AgentSemanticSearch()
    except Exception as e:
        pytest.skip(
            f"Elasticsearch connection failed ({e}); ensure ELASTICSEARCH_URL is reachable to run this test."
        )


def test_basic_search():
    """Test basic search functionality."""
    try:
        result = search_codebase("semantic search", content_type="code")
    except Exception as e:
        pytest.skip(f"Search execution failed ({e}); requires Elasticsearch + populated index.")
    assert result is not None


def main():
    print("🧪 Testing AI Agent Semantic Search Tool")
    print("=" * 50)

    tests = [
        ("Module Import", test_import),
        ("Elasticsearch Connection", test_connection),
        ("Basic Search", test_basic_search),
    ]

    passed = 0
    total = len(tests)

    for test_name, test_func in tests:
        print(f"\n🔍 Testing: {test_name}")
        if test_func():
            passed += 1

    print(f"\n📊 Results: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 All tests passed! The semantic search tool is ready.")
    else:
        print("⚠️  Some tests failed. Check the output above for details.")

    return passed == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
