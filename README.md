# FINWARD Property Service

Central domain service and **Single Source of Truth (SSOT)** for real estate asset data on the FINWARD Intelligence Platform.

## Stack

- Python 3.9+ (3.13 target in production)
- FastAPI, SQLAlchemy 2.0, Alembic
- PostgreSQL + Redis + RabbitMQ + Celery
- DDD, Clean Architecture, CQRS-ready, Event-driven (outbox)

## Quick Start

```bash
# Install
pip3 install -e ".[dev]"

# Run tests (22 domain + 5 API integration)
python3 -m pytest tests/ -v

# Run API locally (SQLite in-memory for dev without Docker)
export DATABASE_URL=sqlite+aiosqlite:///./property.db
export DEBUG=true
uvicorn property_service.main:app --reload --port 8000
```

OpenAPI docs: http://localhost:8000/api/v1/docs

## Docker (full stack)

```bash
cp .env.example .env
make docker-up
```

Services: API `:8000`, PostgreSQL `:5432`, Redis `:6379`, RabbitMQ `:15672`, MinIO `:9001`

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/v1/properties` | Create property |
| POST | `/api/v1/properties/register` | Register from source |
| GET | `/api/v1/properties/{id}` | Get by ID |
| GET | `/api/v1/properties/code/{code}` | Get by code |
| GET | `/api/v1/properties/slug/{slug}` | Get by slug |
| PATCH | `/api/v1/properties/{id}` | Update (optimistic lock) |
| DELETE | `/api/v1/properties/{id}` | Soft delete |
| POST | `/api/v1/properties/{id}/restore` | Restore |
| POST | `/api/v1/properties/{id}/status` | Change status |
| POST | `/api/v1/properties/search` | Search with filters |
| GET | `/api/v1/properties/nearby` | Radius search |
| GET | `/api/v1/properties/statistics` | Tenant statistics |
| POST | `/api/v1/properties/{id}/images` | Upload image metadata |
| GET | `/api/v1/lookups/*` | Property types, statuses, amenities |
| GET | `/health` | Liveness |
| GET | `/health/ready` | Readiness |

## Project Structure

```
src/property_service/
├── domain/           # Aggregates, entities, events, validators (no infra deps)
├── application/      # Use cases / application services
├── infrastructure/   # SQLAlchemy, Redis cache, Celery, outbox
├── presentation/     # FastAPI routes, Pydantic schemas
└── config/           # Settings, logging
```

## Architecture Docs

See [docs/architecture/](docs/architecture/) for the full design package (18 deliverables).

## What's Implemented

- **Phase 1:** Domain model, DB schema, repositories, UoW, DI, health checks, Docker
- **Phase 2:** CRUD API, status machine, audit/outbox events, optimistic locking
- **Phase 3:** Search, nearby, statistics
- **Phase 4:** Image upload metadata (presigned URL stub)
- **Phase 5:** Transactional outbox, Celery skeleton, Redis cache

## What's Next

- PostGIS native geo queries (production)
- Bulk import jobs
- S3/MinIO presigned upload integration
- JWT integration with finward-api identity service
- Elasticsearch read model projection
