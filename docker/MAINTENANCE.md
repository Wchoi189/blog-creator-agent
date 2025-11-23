Maintenance log for Blog Creator Agent docker environment

Status: In progress

Actions performed:

- Hardened `docker/Dockerfile` with additional system packages to build native extensions (cmake, pkg-config, libjpeg-dev, libpng-dev, libsndfile1-dev, ffmpeg, libgl1-mesa-glx, python3-dev, libpython3-dev).
- Adjusted `docker/docker-compose.yml` build contexts to use repository root so Dockerfile COPY can access repo files.
- Made `uv sync` conditional during build and ensured `README.md` is copied into the image.
- Updated service names from `ocr-dev` to `blog-creator-dev` to match project.
- Added Redis service for caching support.
- Added Elasticsearch and Kibana services for search and indexing.
- Updated port mappings for Backend API (8000), Frontend (3000), Redis (6379), Elasticsearch (9200), and Kibana (5601).
- Changed SSH port from 2223 to 2226 to avoid conflicts.
- Removed Chainlit service (no longer used).

Planned next steps:
- Run in-container smoke tests and append results here.
- Verify all services start correctly.
- Test GPU acceleration for ML models (torch, transformers).

Smoke tests (to be filled):

- torch.cuda.is_available():
- uv availability:
- python version and basic import checks:
- Backend API health check:
- Redis connectivity:
- Elasticsearch connectivity:
- Kibana UI accessibility:

Build notes:
- The first build downloads many large CUDA-related wheels (torch, cudnn, etc.) and native libs; expect long first-build times.
- Image base: `nvidia/cuda:12.4.1-devel-ubuntu22.04`.
- Project uses Python 3.10-3.11 as specified in pyproject.toml.

Commands used:
- docker compose -f docker/docker-compose.yml --profile dev up -d --build
- docker ps -a --filter "name=blog-creator"
- docker exec -it blog-creator-dev /bin/bash

Smoke test results (to be executed inside container blog-creator-dev):

- PYTHON: (to be tested)
- TORCH_IMPORT: (to be tested)
- UV_VERSION: (to be tested)
- BACKEND_API: (to be tested)
- REDIS: (to be tested)

Notes:
- Dependencies should be installed at runtime using `uv sync --group dev` inside the container.
- Ensure .env file is properly configured before running services.
- Redis service runs separately and should be started before backend services.
