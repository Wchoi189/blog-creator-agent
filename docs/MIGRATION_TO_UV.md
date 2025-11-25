# Migration from Poetry to uv

This document describes the migration from Poetry to [uv](https://github.com/astral-sh/uv) for Python dependency management.

## Why uv?

- **10-100x faster** than Poetry for dependency resolution and installation
- **Drop-in replacement** for pip, pip-tools, poetry, pyenv, twine, virtualenv, and more
- **Rust-based** for maximum performance
- **Compatible** with existing `pyproject.toml` (PEP 621 format)

## Installation

### Install uv

```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows (PowerShell)
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"

# Or via pip
pip install uv
```

## Migration Steps

### 1. Update pyproject.toml

The `pyproject.toml` has been updated to:
- Remove Poetry-specific sections (`[tool.poetry]`, Poetry build backend)
- Use standard PEP 621 format (already compatible)
- Add FastAPI and backend dependencies
- Configure uv-specific settings in `[tool.uv]`

### 2. Generate Lock File

```bash
# Generate uv.lock file
uv lock

# Install dependencies
uv sync

# Or install with dev dependencies
uv sync --dev
```

### 3. Update Virtual Environment

```bash
# Create virtual environment with uv
uv venv

# Activate (Linux/macOS)
source .venv/bin/activate

# Activate (Windows)
.venv\Scripts\activate

# Install dependencies
uv sync
```

### 4. Update Scripts

Replace Poetry commands with uv equivalents:

| Poetry | uv |
|--------|-----|
| `poetry install` | `uv sync` |
| `poetry add <package>` | `uv add <package>` |
| `poetry remove <package>` | `uv remove <package>` |
| `poetry run <command>` | `uv run <command>` |
| `poetry shell` | `source .venv/bin/activate` (or `uv venv`) |
| `poetry update` | `uv lock --upgrade` then `uv sync` |

### 5. Update CI/CD

If you have CI/CD pipelines, update them:

```yaml
# Before (Poetry)
- run: poetry install
- run: poetry run pytest

# After (uv)
- uses: astral-sh/setup-uv@v1
- run: uv sync
- run: uv run pytest
```

## Running the Application

### Backend

```bash
# Using uv
uv run python -m backend.main

# Or activate venv first
source .venv/bin/activate
python -m backend.main
```

### Development

```bash
# Install dev dependencies
uv sync --dev

# Run linting
uv run ruff check .

# Run tests
uv run pytest
```

## Troubleshooting

### Lock File Conflicts

If you encounter lock file conflicts:

```bash
# Regenerate lock file
uv lock --upgrade
```

### Python Version

uv uses the Python version specified in `.python-version` or `pyproject.toml`:

```bash
# Check Python version
uv python list

# Install specific Python version
uv python install 3.11
```

### Virtual Environment Location

By default, uv creates `.venv` in the project root. To use a different location:

```bash
uv venv --python 3.11 ./venv
```

## Benefits

After migration, you should experience:
- **Faster dependency resolution** (seconds instead of minutes)
- **Faster installation** (parallel downloads and builds)
- **Better error messages** for dependency conflicts
- **Compatible lock file** that works across platforms

## References

- [uv Documentation](https://github.com/astral-sh/uv)
- [uv GitHub](https://github.com/astral-sh/uv)
- [PEP 621 - Python Project Metadata](https://peps.python.org/pep-0621/)

