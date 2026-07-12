# 16. Docker Structure

## Container Images

### API Image (`Dockerfile`)

Multi-stage build for minimal production image.

```dockerfile
# Stage 1: Builder
FROM python:3.13-slim AS builder
WORKDIR /build
RUN pip install --no-cache-dir uv
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev
COPY src/ ./src/
RUN uv pip install --no-deps -e .

# Stage 2: Runtime
FROM python:3.13-slim AS runtime
WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 curl \
    && rm -rf /var/lib/apt/lists/*

RUN groupadd -r appuser && useradd -r -g appuser appuser

COPY --from=builder /build/.venv /app/.venv
COPY --from=builder /build/src /app/src
COPY alembic.ini /app/
COPY migrations/ /app/migrations/
COPY docker/entrypoint.sh /app/entrypoint.sh

ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONPATH="/app/src"
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN chmod +x /app/entrypoint.sh
USER appuser

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

ENTRYPOINT ["/app/entrypoint.sh"]
CMD ["uvicorn", "property_service.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
```

### Worker Image (`Dockerfile.worker`)

```dockerfile
FROM python:3.13-slim AS runtime
WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 libmagic1 \
    && rm -rf /var/lib/apt/lists/*

RUN groupadd -r appuser && useradd -r -g appuser appuser

COPY --from=builder /build/.venv /app/.venv
COPY --from=builder /build/src /app/src

ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONPATH="/app/src"

USER appuser

CMD ["celery", "-A", "property_service.infrastructure.celery.app", "worker", \
     "--loglevel=info", "-Q", "property.default,property.image,property.import,property.geocoding,property.sync,property.outbox,property.maintenance"]
```

### Beat Image

Same as worker with:

```dockerfile
CMD ["celery", "-A", "property_service.infrastructure.celery.app", "beat", "--loglevel=info"]
```

---

## Entrypoint Script

```bash
#!/bin/bash
# docker/entrypoint.sh
set -e

if [ "$RUN_MIGRATIONS" = "true" ]; then
    echo "Running database migrations..."
    alembic upgrade head
fi

if [ "$SEED_LOOKUPS" = "true" ]; then
    echo "Seeding lookup tables..."
    python -m scripts.seed_property_types
fi

exec "$@"
```

---

## Docker Compose (Local Development)

```yaml
# docker/docker-compose.yml

services:
  api:
    build:
      context: ..
      dockerfile: docker/Dockerfile
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql+asyncpg://property:property@postgres:5432/property_db
      - REDIS_URL=redis://redis:6379/0
      - RABBITMQ_URL=amqp://property:property@rabbitmq:5672/
      - S3_ENDPOINT=http://minio:9000
      - S3_ACCESS_KEY=minioadmin
      - S3_SECRET_KEY=minioadmin
      - S3_BUCKET=property-media
      - JWT_JWKS_URL=http://host.docker.internal:8080/.well-known/jwks.json
      - RUN_MIGRATIONS=true
      - SEED_LOOKUPS=true
      - LOG_LEVEL=DEBUG
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
      rabbitmq:
        condition: service_healthy
      minio:
        condition: service_started
    volumes:
      - ../src:/app/src  # hot reload in dev
    command: >
      uvicorn property_service.main:app
      --host 0.0.0.0 --port 8000 --reload

  worker:
    build:
      context: ..
      dockerfile: docker/Dockerfile.worker
    environment:
      - DATABASE_URL=postgresql+asyncpg://property:property@postgres:5432/property_db
      - REDIS_URL=redis://redis:6379/0
      - RABBITMQ_URL=amqp://property:property@rabbitmq:5672/
      - S3_ENDPOINT=http://minio:9000
      - S3_ACCESS_KEY=minioadmin
      - S3_SECRET_KEY=minioadmin
      - S3_BUCKET=property-media
    depends_on:
      - postgres
      - redis
      - rabbitmq
      - minio
    volumes:
      - ../src:/app/src

  beat:
    build:
      context: ..
      dockerfile: docker/Dockerfile.worker
    command: >
      celery -A property_service.infrastructure.celery.app beat --loglevel=info
    environment:
      - DATABASE_URL=postgresql+asyncpg://property:property@postgres:5432/property_db
      - REDIS_URL=redis://redis:6379/0
      - RABBITMQ_URL=amqp://property:property@rabbitmq:5672/
    depends_on:
      - redis
      - rabbitmq

  postgres:
    image: postgis/postgis:16-3.4
    environment:
      POSTGRES_USER: property
      POSTGRES_PASSWORD: property
      POSTGRES_DB: property_db
    ports:
      - "5432:5432"
    volumes:
      - pgdata:/var/lib/postgresql/data
      - ./init-db.sql:/docker-entrypoint-initdb.d/01-init.sql
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U property -d property_db"]
      interval: 5s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 5s
      timeout: 3s
      retries: 5

  rabbitmq:
    image: rabbitmq:3.13-management-alpine
    ports:
      - "5672:5672"
      - "15672:15672"
    environment:
      RABBITMQ_DEFAULT_USER: property
      RABBITMQ_DEFAULT_PASS: property
    healthcheck:
      test: ["CMD", "rabbitmq-diagnostics", "check_running"]
      interval: 10s
      timeout: 5s
      retries: 5

  minio:
    image: minio/minio:latest
    ports:
      - "9000:9000"
      - "9001:9001"
    environment:
      MINIO_ROOT_USER: minioadmin
      MINIO_ROOT_PASSWORD: minioadmin
    command: server /data --console-address ":9001"
    volumes:
      - miniodata:/data

  # One-time bucket creation
  minio-init:
    image: minio/mc:latest
    depends_on:
      - minio
    entrypoint: >
      /bin/sh -c "
      sleep 3;
      mc alias set local http://minio:9000 minioadmin minioadmin;
      mc mb --ignore-existing local/property-media;
      exit 0;
      "

volumes:
  pgdata:
  miniodata:
```

---

## Init DB Script

```sql
-- docker/init-db.sql
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "postgis";
CREATE SCHEMA IF NOT EXISTS property;
SET search_path TO property, public;
```

---

## Production Compose Override

```yaml
# docker/docker-compose.prod.yml
services:
  api:
    build:
      target: runtime
    restart: always
    deploy:
      replicas: 3
      resources:
        limits:
          cpus: "2"
          memory: 1G
    environment:
      - RUN_MIGRATIONS=false
      - LOG_LEVEL=INFO
    volumes: []  # no source mount
    command: >
      uvicorn property_service.main:app
      --host 0.0.0.0 --port 8000 --workers 4

  worker:
    restart: always
    deploy:
      replicas: 2
    volumes: []
```

---

## Makefile Targets

```makefile
.PHONY: up down build migrate test lint

up:
	docker compose -f docker/docker-compose.yml up -d

down:
	docker compose -f docker/docker-compose.yml down

build:
	docker compose -f docker/docker-compose.yml build

migrate:
	docker compose -f docker/docker-compose.yml exec api alembic upgrade head

test:
	docker compose -f docker/docker-compose.yml exec api pytest

lint:
	ruff check src/ tests/
	mypy src/

logs:
	docker compose -f docker/docker-compose.yml logs -f api worker
```

---

## Image Tagging

| Tag | When |
|-----|------|
| `property-service:latest` | Latest main build |
| `property-service:{git-sha}` | Every CI build |
| `property-service:v{semver}` | Release tags |

---

## .dockerignore

```
.git
.env
.venv
__pycache__
*.pyc
.pytest_cache
.mypy_cache
.ruff_cache
tests/
docs/
*.md
docker-compose*.yml
```
