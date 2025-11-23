# AI Agent Semantic Search Tool

Provides AI agents with powerful semantic search capabilities across the entire codebase, documentation, and training data using Elasticsearch with Korean language support.

## Features

- **Unified Search**: Search across code, documentation, and data in one place
- **Korean Language Support**: Optimized for Korean text with Nori analyzer
- **Multiple Content Types**: Code, documentation, configuration files, scripts
- **Intelligent Chunking**: Smart content splitting for better search results
- **AI Agent Integration**: Easy-to-use functions for automated workflows

## Quick Start

### 1. Prerequisites
- Elasticsearch running on `http://host.docker.internal:9201` (or via `ELASTICSEARCH_URL` env var)
- Python dependencies installed

### 2. Index the Codebase
```bash
cd agent_interface/tools/semantic_search
python setup_agent_search.py --index
```

### 3. Test Search Functionality
```bash
# Test with a sample query
python setup_agent_search.py --query "Korean grammar correction"

# Run general tests
python setup_agent_search.py --test
```

## Usage for AI Agents

### Basic Search
```python
from agent.tools.semantic_search.agent_semantic_search import AgentSemanticSearch

search = AgentSemanticSearch()
results = search.semantic_search("find similar sentences", top_k=5)

for result in results:
    print(f"File: {result.file_path}")
    print(f"Content: {result.content[:200]}...")
    print(f"Score: {result.score:.3f}")
```

### Specialized Searches
```python
# Search only code
code_results = search.search_code("def function_name")

# Search only documentation
doc_results = search.search_documentation("API usage")

# Find similar code patterns
similar_code = search.find_similar_code("for item in items:")

# Explain concepts
explanations = search.explain_concept("semantic search")
```

### Convenience Function
```python
from agent.tools.semantic_search.agent_semantic_search import search_codebase

# Simple search interface
results = search_codebase("training data processing", content_type="code")
print(results)
```

## Architecture

### Content Types
- **code**: Python, JavaScript, shell scripts
- **documentation**: Markdown, text files
- **configuration**: JSON, YAML, config files
- **data**: CSV, SQL, data files

### Indexing Strategy
- **Code**: Split by lines (20 lines per chunk)
- **Documentation**: Split by paragraphs
- **Other**: Split by logical units

### Search Features
- **Semantic Matching**: Uses Elasticsearch text analysis
- **Korean Support**: Nori tokenizer with part-of-speech filtering
- **Relevance Scoring**: Cosine similarity for embeddings
- **Filtering**: By content type, language, file path

## Configuration

### Environment Variables
```bash
export ELASTICSEARCH_URL=http://host.docker.internal:9201
```

### Index Settings
- **Index Name**: `agent_codebase` (configurable)
- **Analyzer**: Nori → CJK → Standard (automatic fallback)
- **Vector Dimensions**: 768 (for sentence-transformers compatibility)

## Integration Examples

### With Cursor/VS Code
```json
{
  "mcpServers": {
    "semantic-search": {
      "command": "python",
      "args": ["-m", "agent.tools.semantic_search.agent_semantic_search"],
      "env": {
        "ELASTICSEARCH_URL": "http://host.docker.internal:9201"
      }
    }
  }
}
```

### With Claude Desktop
```json
{
  "mcpServers": {
    "codebase-search": {
      "command": "python",
      "args": ["-c", "from agent.tools.semantic_search.agent_semantic_search import search_codebase; import sys; print(search_codebase(sys.argv[1]))"],
      "args": ["query"]
    }
  }
}
```

## Performance Notes

- **Indexing**: ~1-5 minutes for typical codebase
- **Search**: <100ms for most queries
- **Memory**: ~500MB for large codebases
- **Storage**: ~2-5x original codebase size

## Troubleshooting

### Connection Issues
```bash
# Check Elasticsearch status
curl http://host.docker.internal:9201/_cluster/health

# Test with setup script
python setup_agent_search.py --test
```

### Indexing Problems
```bash
# Clear and reindex
curl -X DELETE http://host.docker.internal:9201/agent_codebase
python setup_agent_search.py --index
```

### Search Quality Issues
- Ensure Nori plugin is installed for Korean text
- Check that content was properly indexed
- Try different query formulations

## Migration from Seroost

This tool replaces the previous Seroost-based implementation with:

- **Better Korean Support**: Elasticsearch Nori analyzer
- **Unified Architecture**: Single tool for all content types
- **Production Ready**: Scalable and reliable
- **AI Agent Optimized**: Simplified interfaces for automation

## Future Enhancements

- **Hybrid Search**: Combine semantic + keyword search
- **Code Understanding**: AST-based code analysis
- **Multi-language**: Support for additional languages
- **Caching**: Query result caching for performance
- **Feedback Loop**: Learning from user preferences