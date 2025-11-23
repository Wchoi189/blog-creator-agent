# Part 4: Production Deployment

## Status: ⏸️ Pending (0%)

**Goal**: Create production-ready deployment infrastructure with Docker, CI/CD, and monitoring.

## Phase 4.1: Containerization

### Task 4.1.1: Backend Dockerfile

**Objective**: Create optimized Docker image for FastAPI backend

**Files**:
- `backend/Dockerfile`
- `backend/.dockerignore`

**Multi-stage build**:
```dockerfile
# backend/Dockerfile

# Stage 1: Builder
FROM python:3.11-slim as builder

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# Stage 2: Runtime
FROM python:3.11-slim

WORKDIR /app

# Copy Python dependencies from builder
COPY --from=builder /root/.local /root/.local
ENV PATH=/root/.local/bin:$PATH

# Copy application code
COPY . .

# Create non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Expose port
EXPOSE 8000

# Run application
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**Optimizations**:
- Multi-stage build (smaller image size)
- Layer caching for faster builds
- Non-root user for security
- Health check included

### Task 4.1.2: Frontend Dockerfile

**Objective**: Create optimized Docker image for Next.js frontend

**Files**:
- `frontend/Dockerfile`
- `frontend/.dockerignore`

**Multi-stage build**:
```dockerfile
# frontend/Dockerfile

# Stage 1: Dependencies
FROM node:20-alpine AS deps

WORKDIR /app

# Copy package files
COPY package.json package-lock.json* ./

# Install dependencies
RUN npm ci --only=production

# Stage 2: Builder
FROM node:20-alpine AS builder

WORKDIR /app

# Copy dependencies
COPY --from=deps /app/node_modules ./node_modules
COPY . .

# Build application
ENV NEXT_TELEMETRY_DISABLED 1
RUN npm run build

# Stage 3: Runner
FROM node:20-alpine AS runner

WORKDIR /app

ENV NODE_ENV production
ENV NEXT_TELEMETRY_DISABLED 1

# Create non-root user
RUN addgroup --system --gid 1001 nodejs
RUN adduser --system --uid 1001 nextjs

# Copy built application
COPY --from=builder /app/public ./public
COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static

USER nextjs

EXPOSE 3000

ENV PORT 3000
ENV HOSTNAME "0.0.0.0"

CMD ["node", "server.js"]
```

**Configuration**:
```javascript
// next.config.js
module.exports = {
  output: 'standalone', // Enable for Docker
  // ... other config
};
```

### Task 4.1.3: Docker Compose

**Objective**: Local development environment with all services

**Files**:
- `docker-compose.yml`
- `docker-compose.prod.yml`

**Development setup**:
```yaml
# docker-compose.yml
version: '3.8'

services:
  # Backend API
  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://user:pass@postgres:5432/blogdb
      - REDIS_URL=redis://redis:6379
      - ELASTICSEARCH_URL=http://elasticsearch:9200
    volumes:
      - ./backend:/app
      - ./data/chromadb:/app/data/chromadb
    depends_on:
      - postgres
      - redis
      - elasticsearch
    command: uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload

  # Frontend
  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
      target: deps  # Only deps stage for dev
    ports:
      - "3000:3000"
    environment:
      - NEXT_PUBLIC_API_URL=http://localhost:8000
    volumes:
      - ./frontend:/app
      - /app/node_modules
      - /app/.next
    command: npm run dev

  # PostgreSQL database
  postgres:
    image: postgres:16-alpine
    environment:
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=pass
      - POSTGRES_DB=blogdb
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

  # Redis cache
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data

  # ElasticSearch
  elasticsearch:
    image: docker.elastic.co/elasticsearch/elasticsearch:8.11.0
    environment:
      - discovery.type=single-node
      - xpack.security.enabled=false
      - "ES_JAVA_OPTS=-Xms512m -Xmx512m"
    ports:
      - "9200:9200"
    volumes:
      - elasticsearch_data:/usr/share/elasticsearch/data

  # Nginx reverse proxy
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf:ro
      - ./nginx/ssl:/etc/nginx/ssl:ro
    depends_on:
      - backend
      - frontend

volumes:
  postgres_data:
  redis_data:
  elasticsearch_data:
```

**Production setup**:
```yaml
# docker-compose.prod.yml
version: '3.8'

services:
  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    restart: always
    environment:
      - DATABASE_URL=${DATABASE_URL}
      - REDIS_URL=${REDIS_URL}
      - SECRET_KEY=${SECRET_KEY}
    deploy:
      replicas: 2
      resources:
        limits:
          cpus: '1'
          memory: 1G

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    restart: always
    deploy:
      replicas: 2
      resources:
        limits:
          cpus: '0.5'
          memory: 512M
```

### Task 4.1.4: Nginx Configuration

**Objective**: Reverse proxy and SSL termination

**Files**:
- `nginx/nginx.conf`

```nginx
# nginx/nginx.conf
events {
    worker_connections 1024;
}

http {
    upstream backend {
        server backend:8000;
    }

    upstream frontend {
        server frontend:3000;
    }

    # Redirect HTTP to HTTPS
    server {
        listen 80;
        server_name example.com;
        return 301 https://$server_name$request_uri;
    }

    # HTTPS server
    server {
        listen 443 ssl http2;
        server_name example.com;

        ssl_certificate /etc/nginx/ssl/cert.pem;
        ssl_certificate_key /etc/nginx/ssl/key.pem;

        # API routes
        location /api/ {
            proxy_pass http://backend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        # WebSocket
        location /ws/ {
            proxy_pass http://backend;
            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection "upgrade";
        }

        # Frontend
        location / {
            proxy_pass http://frontend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
        }
    }
}
```

## Phase 4.2: CI/CD Pipeline

### Task 4.2.1: GitHub Actions Workflow

**Objective**: Automated testing, building, and deployment

**Files**:
- `.github/workflows/ci.yml`
- `.github/workflows/deploy.yml`

**CI Workflow**:
```yaml
# .github/workflows/ci.yml
name: CI

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  test-backend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          cd backend
          pip install -r requirements.txt
          pip install pytest pytest-cov

      - name: Run tests
        run: |
          cd backend
          pytest --cov=backend --cov-report=xml

      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          files: ./backend/coverage.xml

  test-frontend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Set up Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '20'

      - name: Install dependencies
        run: |
          cd frontend
          npm ci

      - name: Run tests
        run: |
          cd frontend
          npm test -- --coverage

      - name: Run E2E tests
        run: |
          cd frontend
          npm run test:e2e

  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Lint backend
        run: |
          cd backend
          pip install ruff
          ruff check .

      - name: Lint frontend
        run: |
          cd frontend
          npm ci
          npm run lint

  build:
    needs: [test-backend, test-frontend, lint]
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v2

      - name: Login to Docker Hub
        uses: docker/login-action@v2
        with:
          username: ${{ secrets.DOCKER_USERNAME }}
          password: ${{ secrets.DOCKER_PASSWORD }}

      - name: Build and push backend
        uses: docker/build-push-action@v4
        with:
          context: ./backend
          push: true
          tags: |
            ${{ secrets.DOCKER_USERNAME }}/blog-creator-backend:latest
            ${{ secrets.DOCKER_USERNAME }}/blog-creator-backend:${{ github.sha }}

      - name: Build and push frontend
        uses: docker/build-push-action@v4
        with:
          context: ./frontend
          push: true
          tags: |
            ${{ secrets.DOCKER_USERNAME }}/blog-creator-frontend:latest
            ${{ secrets.DOCKER_USERNAME }}/blog-creator-frontend:${{ github.sha }}
```

**Deploy Workflow**:
```yaml
# .github/workflows/deploy.yml
name: Deploy

on:
  push:
    branches: [main]
  workflow_dispatch:

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Deploy to production
        uses: appleboy/ssh-action@master
        with:
          host: ${{ secrets.DEPLOY_HOST }}
          username: ${{ secrets.DEPLOY_USER }}
          key: ${{ secrets.DEPLOY_KEY }}
          script: |
            cd /opt/blog-creator
            docker-compose pull
            docker-compose up -d
            docker system prune -f
```

### Task 4.2.2: Automated Testing

**Backend tests**:
```python
# backend/tests/test_api.py
import pytest
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_create_document():
    response = client.post(
        "/api/v1/documents/upload",
        files={"file": ("test.pdf", b"fake pdf content", "application/pdf")}
    )
    assert response.status_code == 201
    assert "id" in response.json()
```

**Frontend tests**:
```typescript
// frontend/src/app/__tests__/page.test.tsx
import { render, screen } from '@testing-library/react';
import Home from '../page';

test('renders home page', () => {
  render(<Home />);
  expect(screen.getByText(/Blog Creator/i)).toBeInTheDocument();
});
```

## Phase 4.3: Monitoring & Logging

### Task 4.3.1: Prometheus Metrics

**Objective**: Expose application metrics

**Files**:
- `backend/core/metrics.py`

**Implementation**:
```python
# backend/core/metrics.py
from prometheus_client import Counter, Histogram, generate_latest
from fastapi import FastAPI

# Define metrics
request_count = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status']
)

request_duration = Histogram(
    'http_request_duration_seconds',
    'HTTP request duration',
    ['method', 'endpoint']
)

document_uploads = Counter(
    'document_uploads_total',
    'Total document uploads',
    ['file_type']
)

blog_generations = Counter(
    'blog_generations_total',
    'Total blog generations',
    ['status']
)

def setup_metrics(app: FastAPI):
    @app.get("/metrics")
    async def metrics():
        return Response(
            generate_latest(),
            media_type="text/plain"
        )
```

### Task 4.3.2: Grafana Dashboards

**Objective**: Visualize application metrics

**Files**:
- `monitoring/grafana/dashboards/app-dashboard.json`
- `monitoring/prometheus/prometheus.yml`

**Dashboard panels**:
- Request rate (requests/sec)
- Response time (p50, p95, p99)
- Error rate
- Document uploads
- Active users
- Database connections
- Memory usage
- CPU usage

**Prometheus config**:
```yaml
# monitoring/prometheus/prometheus.yml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'backend'
    static_configs:
      - targets: ['backend:8000']

  - job_name: 'frontend'
    static_configs:
      - targets: ['frontend:3000']
```

### Task 4.3.3: Centralized Logging

**Objective**: Aggregate logs from all services

**Stack**: ELK (Elasticsearch, Logstash, Kibana)

**Files**:
- `backend/core/logging.py`

**Structured logging**:
```python
# backend/core/logging.py
import logging
import json
from datetime import datetime

class JSONFormatter(logging.Formatter):
    def format(self, record):
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
        }

        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)

        return json.dumps(log_data)

# Setup
handler = logging.StreamHandler()
handler.setFormatter(JSONFormatter())

logger = logging.getLogger("blog_creator")
logger.addHandler(handler)
logger.setLevel(logging.INFO)
```

### Task 4.3.4: Error Tracking (Sentry)

**Objective**: Track and monitor errors in production

**Files**:
- `backend/main.py` (add Sentry)
- `frontend/src/app/layout.tsx` (add Sentry)

**Backend integration**:
```python
# backend/main.py
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration

sentry_sdk.init(
    dsn=settings.SENTRY_DSN,
    integrations=[FastApiIntegration()],
    traces_sample_rate=0.1,
    environment=settings.ENVIRONMENT,
)
```

**Frontend integration**:
```typescript
// frontend/src/app/layout.tsx
import * as Sentry from '@sentry/nextjs';

Sentry.init({
  dsn: process.env.NEXT_PUBLIC_SENTRY_DSN,
  tracesSampleRate: 0.1,
  environment: process.env.NODE_ENV,
});
```

## Phase 4.4: Security Hardening

### Task 4.4.1: SSL/TLS Configuration

**Features**:
- Let's Encrypt certificates
- Auto-renewal
- Strong cipher suites
- HSTS headers

### Task 4.4.2: Security Headers

**Implementation**:
```python
# backend/core/middleware.py
from fastapi.middleware.cors import CORSMiddleware

@app.middleware("http")
async def add_security_headers(request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    return response
```

### Task 4.4.3: Rate Limiting

**Implementation**: Redis-based rate limiter

### Task 4.4.4: Secrets Management

**Tools**: HashiCorp Vault or AWS Secrets Manager

## Deployment Checklist

- [ ] Environment variables configured
- [ ] Database migrations applied
- [ ] SSL certificates installed
- [ ] Firewall rules configured
- [ ] Backup strategy implemented
- [ ] Monitoring dashboards setup
- [ ] Alerts configured
- [ ] Load testing completed
- [ ] Security audit passed
- [ ] Documentation updated

## Success Criteria

- ✅ Docker images build successfully
- ✅ Services start with docker-compose
- ✅ CI/CD pipeline runs without errors
- ✅ Automated tests pass
- ✅ Metrics exposed and visible in Grafana
- ✅ Logs aggregated in Kibana
- ✅ Error tracking working in Sentry
- ✅ Load testing shows < 2s response time
- ✅ Zero-downtime deployment working

## Next Steps

After completing Part 4:
1. Update progress to 100% in `docs/plans/README.md`
2. Commit: "feat: add production deployment (Part 4)"
3. Create pull request for review
4. Deploy to production
5. Monitor and optimize
