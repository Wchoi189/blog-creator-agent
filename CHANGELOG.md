# Changelog

## 📋 Guidelines

**Keep entries ultra-concise.** This changelog should be scannable and brief.

- **One line per change** - Use bullet points, avoid paragraphs
- **Reference extended summaries** - Link to PRs, issues, or detailed docs for full context
- **Group by type** - Use standard categories: Added, Changed, Fixed, Removed, Security
- **Datestamps** - Format as `YYYY-MM-DD HH:MM (KST)` using Asia/Seoul time
- **Version format** - Follow [Semantic Versioning](https://semver.org/): MAJOR.MINOR.PATCH
- **Date format** - Use YYYY-MM-DD

**Example:**
```markdown
### [2.1.0] - 2025-11-24 23:01 (KST)
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
- @qwen syntax for AI agent chat integration with Qwen Coder
- Command interpreter script (.qwen/qwen-chat.sh) for conversational AI workflows
- FastAPI and backend dependencies to pyproject.toml
- .python-version file for uv compatibility

### Changed
- Migrated dependency management from Poetry to uv
- Updated pyproject.toml to use PEP 621 format with uv build system
- Updated README.md to reference uv instead of Poetry
- Updated .gitignore to track .python-version (needed for uv)

### Removed
- Poetry-specific sections from pyproject.toml ([tool.poetry], Poetry build backend)

### Security
- Updated frontend Next.js/axios/eslint deps to resolve npm audit findings
- **[2025-11-26]** Comprehensive security audit completed ([Audit Report](docs/audit/AUDIT_REPORT_2025-11-26.md))
- **[2025-11-26]** Resolved 21 Python dependency vulnerabilities
  - certifi: 2023.11.17 → 2025.11.12
  - configobj: 5.0.8 → 5.0.9
  - cryptography: 41.0.7 → 46.0.3
  - idna: 3.6 → 3.11
  - jinja2: 3.1.2 → 3.1.6
  - pip: 24.0 → 25.3
  - requests: 2.31.0 → 2.32.5
  - setuptools: 68.1.2 → 80.9.0
  - twisted: 24.3.0 → 25.5.0
  - urllib3: 2.0.7 → 2.5.0
- **[2025-11-26]** Added SECURITY.md with security policy and best practices
- **[2025-11-26]** Verified 0 vulnerabilities in frontend dependencies (npm audit)
- **[2025-11-26]** Verified 0 vulnerabilities in backend dependencies (pip-audit)

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

