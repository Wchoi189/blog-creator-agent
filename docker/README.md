# Docker Development Environment for Blog Creator Agent

This directory contains Docker configuration files for running the Blog Creator Agent in a containerized development environment with GPU support.

## Quick Start

### Prerequisites

- Docker and Docker Compose installed
- NVIDIA Docker runtime (nvidia-container-toolkit) for GPU support
- Git

### Build and Run

```bash
# From the project root directory
cd /path/to/blog-creator-agent

# Build and start the development container
docker compose -f docker/docker-compose.yml --profile dev up -d --build
```

**Note**: The first build can be large and slow as it downloads CUDA-enabled wheels and native extensions (torch, transformers, etc.).

### Access the Container

```bash
# Open a shell inside the container
docker exec -it blog-creator-dev /bin/bash

# Or use the Makefile
make -C docker shell
```

### Available Services

Once the containers are running, you can access:

- **Backend API**: http://localhost:8000 (FastAPI)
- **Frontend**: http://localhost:3000 (Next.js)
- **Redis**: localhost:6379
- **Redis Insight**: http://localhost:8001
- **Elasticsearch**: http://localhost:9200
- **Kibana**: http://localhost:5601
- **SSH**: `ssh -p 2226 vscode@localhost`

### Common Commands

```bash
# Using Makefile (from project root)
make -C docker help          # Show all available commands
make -C docker build         # Build the image
make -C docker up            # Start containers
make -C docker down          # Stop containers
make -C docker logs          # View logs
make -C docker shell         # Open shell in container
make -C docker rebuild       # Rebuild from scratch

# Using Docker Compose directly
docker compose -f docker/docker-compose.yml --profile dev up -d
docker compose -f docker/docker-compose.yml --profile dev down
docker compose -f docker/docker-compose.yml --profile dev logs -f
```

### Setup Inside Container

After entering the container, set up the project:

```bash
# Sync dependencies with uv
uv sync --group dev

# Run the backend API
uv run python -m backend.main

# Or run the frontend (from frontend directory)
cd frontend
npm install
npm run dev
```

### Elasticsearch and Kibana

The Docker setup includes Elasticsearch and Kibana for search and indexing capabilities:

- **Elasticsearch**: Available at http://localhost:9200
  - Used for document indexing and search
  - Configured with security disabled for development
  - Memory allocation: 512MB (adjustable via `ES_JAVA_OPTS`)

- **Kibana**: Available at http://localhost:5601
  - Web UI for Elasticsearch data visualization
  - Connect to Elasticsearch automatically
  - Useful for debugging and monitoring search queries

To verify Elasticsearch is running:
```bash
curl http://localhost:9200
```

To start only Elasticsearch/Kibana services:
```bash
make -C docker elasticsearch
make -C docker kibana
```

### Troubleshooting

- **Build failures for native extensions**: Ensure all required system packages are in `docker/Dockerfile`. You may need to run `uv sync` inside the container after building.

- **GPU not available**: Verify NVIDIA Docker runtime is installed:
  ```bash
  docker run --rm --gpus all nvidia/cuda:12.4.1-base-ubuntu22.04 nvidia-smi
  ```

- **Port conflicts**: If ports are already in use, modify the port mappings in `docker/docker-compose.yml`.

- **Permission issues**: The container runs as user `vscode` (UID 1000). Ensure your user has access to mounted volumes.

### Clean Up

```bash
# Stop and remove containers, networks, and volumes
docker compose -f docker/docker-compose.yml --profile dev down -v

# Or using Makefile
make -C docker clean
```
