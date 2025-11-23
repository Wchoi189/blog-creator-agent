# Changelog

## 📋 Guidelines

**Keep entries ultra-concise.** This changelog should be scannable and brief.

- **One line per change** - Use bullet points, avoid paragraphs
- **Reference extended summaries** - Link to PRs, issues, or detailed docs for full context
- **Group by type** - Use standard categories: Added, Changed, Fixed, Removed, Security
- **Version format** - Follow [Semantic Versioning](https://semver.org/): MAJOR.MINOR.PATCH
- **Date format** - Use YYYY-MM-DD

**Example:**
```markdown
### [2.1.0] - 2025-01-15
- Added WebSocket support for real-time updates ([#123](https://github.com/...))
- Fixed authentication token expiration issue ([#124](https://github.com/...))
- Changed default port from 8000 to 8080
```

For detailed migration notes, see [docs/plans/README.md](docs/plans/README.md).

---

## [Unreleased]

### Added
- CHANGELOG.md template with concise entry guidelines
- Migration guide from Poetry to uv (docs/MIGRATION_TO_UV.md)
- FastAPI and backend dependencies to pyproject.toml
- .python-version file for uv compatibility

### Changed
- Migrated dependency management from Poetry to uv
- Updated pyproject.toml to use PEP 621 format with uv build system
- Updated README.md to reference uv instead of Poetry
- Updated .gitignore to track .python-version (needed for uv)

### Removed
- Poetry-specific sections from pyproject.toml ([tool.poetry], Poetry build backend)

---

## [2.0.0] - 2025-01-XX

### Added
- FastAPI backend with 20+ REST endpoints
- Next.js 14 frontend with TypeScript
- JWT + API key authentication
- Document processing (PDF, audio, images)
- Tiptap rich text editor
- WebSocket real-time communication
- Session management
- Document upload with drag-and-drop
- Dashboard with statistics

### Changed
- Migrated from Chainlit to Next.js + FastAPI architecture
- Migrated dependency management from Poetry to uv
- Updated project structure (backend/ and frontend/ directories)

### Removed
- Chainlit UI framework
- Poetry dependency manager

---

## [1.0.0] - 2024-XX-XX

### Added
- Initial Chainlit-based implementation
- RAG pipeline with LangChain/LangGraph
- Document processing (PDF, audio, images)
- GitHub Pages publishing
- Vector store integration (ChromaDB)

---

[Unreleased]: https://github.com/Wchoi189/blog-creator-agent/compare/v2.0.0...HEAD
[2.0.0]: https://github.com/Wchoi189/blog-creator-agent/compare/v1.0.0...v2.0.0
[1.0.0]: https://github.com/Wchoi189/blog-creator-agent/releases/tag/v1.0.0

