# 18. Development Roadmap

## Overview

Incremental delivery in 6 phases over ~24 weeks. Each phase produces a deployable, testable increment. No phase sacrifices the architectural foundation.

```
Phase 1 ──► Phase 2 ──► Phase 3 ──► Phase 4 ──► Phase 5 ──► Phase 6
Foundation   Core CRUD   Search      Media       Events      Enterprise
(4 weeks)    (4 weeks)   (4 weeks)   (4 weeks)   (4 weeks)   (4 weeks)
```

---

## Phase 1: Foundation (Weeks 1–4)

**Goal:** Project scaffold, domain model, database, basic API skeleton.

### Deliverables

- [ ] Project scaffold (pyproject.toml, folder structure, Docker Compose)
- [ ] Configuration (Pydantic Settings, structured logging)
- [ ] PostgreSQL schema + Alembic migrations (all tables)
- [ ] PostGIS setup, seed property types and amenities
- [ ] Domain model: Property aggregate, value objects, enums, exceptions
- [ ] Repository interfaces + SQLAlchemy implementations
- [ ] Unit of Work pattern
- [ ] Domain ↔ ORM mappers
- [ ] DI container wiring
- [ ] Health check endpoints
- [ ] JWT middleware (stub/mock for local dev)
- [ ] Exception handlers
- [ ] Unit tests: domain model, validators, state machine

### Exit Criteria

- `docker compose up` starts all services
- Migrations run successfully
- Health checks pass
- Domain unit tests > 90% coverage
- CI pipeline: lint + unit tests

---

## Phase 2: Core CRUD (Weeks 5–8)

**Goal:** Full property lifecycle — create, read, update, delete, status management.

### Deliverables

- [ ] `POST /api/v1/properties` — manual creation
- [ ] `GET /api/v1/properties/{id}` — with includes
- [ ] `GET /api/v1/properties/code/{code}`
- [ ] `GET /api/v1/properties/slug/{slug}`
- [ ] `PUT /api/v1/properties/{id}` — full update
- [ ] `PATCH /api/v1/properties/{id}` — partial update
- [ ] `DELETE /api/v1/properties/{id}` — soft delete
- [ ] `POST /api/v1/properties/{id}/restore`
- [ ] `POST /api/v1/properties/{id}/status` — state machine
- [ ] Property code and slug generation
- [ ] Optimistic locking (version)
- [ ] Audit log on every mutation
- [ ] Price history on price changes
- [ ] Status history on status changes
- [ ] Version snapshots on significant changes
- [ ] `POST /api/v1/properties/register` — from address/coordinates
- [ ] Lookup endpoints (property types, amenities, statuses)
- [ ] Integration tests: repository + API
- [ ] OpenAPI spec generation

### Exit Criteria

- Full CRUD via API with JWT auth
- Audit trail verifiable
- Optimistic locking tested (409 on conflict)
- Status state machine fully tested
- API integration tests > 80% endpoint coverage

---

## Phase 3: Search (Weeks 9–12)

**Goal:** Powerful property search with geo, filters, pagination, caching.

### Deliverables

- [ ] `POST /api/v1/properties/search` — full filter support
- [ ] `GET /api/v1/properties/search` — query param search
- [ ] `GET /api/v1/properties/nearby` — radius search
- [ ] `GET /api/v1/properties/map` — bounding box / clusters
- [ ] PostgreSQL full-text search (tsvector)
- [ ] PostGIS queries (radius, bounding box, polygon)
- [ ] Sorting (price, area, date, distance)
- [ ] Pagination with total counts
- [ ] Faceted search (optional, by type/status/province)
- [ ] Redis search result caching
- [ ] `GET /api/v1/properties/statistics`
- [ ] Performance tests: search < 200ms p95 for 1M records
- [ ] Search cache invalidation on property mutations

### Exit Criteria

- All search filter types working
- Geo search accurate within 1% of PostGIS reference
- Cache hit ratio > 70% in load test
- Search performance benchmarks documented

---

## Phase 4: Media & Import (Weeks 13–16)

**Goal:** Image/document management, bulk import, external source registration.

### Deliverables

- [ ] S3/MinIO object storage integration
- [ ] Image upload flow (presigned URL → confirm → process)
- [ ] Thumbnail generation (Celery task)
- [ ] Image reorder, delete, primary selection
- [ ] Document upload, verify, delete
- [ ] `POST /api/v1/properties/register` — listing URL import
- [ ] Listing adapter: sahibinden (first provider)
- [ ] `POST /api/v1/properties/bulk/import`
- [ ] `PATCH /api/v1/properties/bulk/update`
- [ ] `DELETE /api/v1/properties/bulk`
- [ ] Bulk job status polling
- [ ] Geocoding tasks (forward + reverse)
- [ ] Celery worker deployment
- [ ] Idempotency key support on POST endpoints

### Exit Criteria

- End-to-end image upload and thumbnail generation
- Bulk import of 500 properties completes < 10 min
- Listing URL import creates valid property
- Geocoding populates coordinates from address

---

## Phase 5: Events & Integration (Weeks 17–20)

**Goal:** Event-driven architecture, outbox, downstream consumer readiness.

### Deliverables

- [ ] Domain events on all mutations
- [ ] Transactional outbox table + processor
- [ ] RabbitMQ publisher (CloudEvents format)
- [ ] Event-driven cache invalidation
- [ ] `GET /api/v1/properties/{id}/history/*` endpoints
- [ ] `GET /api/v1/properties/{id}/versions/*` endpoints
- [ ] `GET /api/v1/properties/{id}/audit-logs` (admin)
- [ ] Ownership management endpoints
- [ ] Metadata management endpoints
- [ ] External listing sync (Celery beat)
- [ ] Rate limiting middleware
- [ ] API key authentication (partner tier)
- [ ] OpenTelemetry tracing
- [ ] Prometheus metrics
- [ ] Consumer documentation for downstream services

### Exit Criteria

- Events published reliably (outbox → RabbitMQ)
- Zero event loss in chaos test (kill worker mid-publish)
- Downstream consumer can subscribe and process events
- Rate limiting enforced per tier
- Distributed tracing visible in Jaeger

---

## Phase 6: Enterprise & Production (Weeks 21–24)

**Goal:** Production hardening, enterprise features, scale validation.

### Deliverables

- [ ] Multi-tenancy hardening (row-level security option)
- [ ] RBAC full implementation (all permissions)
- [ ] Partner API (scoped read access)
- [ ] Enterprise API (bulk, statistics, audit)
- [ ] Property merge / deduplication service
- [ ] Additional listing adapters (emlakjet, hepsiemlak)
- [ ] Read replica support for search queries
- [ ] Database partitioning (audit logs)
- [ ] Kubernetes deployment manifests / Helm chart
- [ ] Production Docker Compose
- [ ] Load testing: 1M properties, 1000 RPS
- [ ] Disaster recovery drill
- [ ] Security audit / penetration test
- [ ] API documentation portal
- [ ] SDK generation (OpenAPI → TypeScript, Dart)
- [ ] Integration with finward-api (property_id on real_estate holdings)
- [ ] Elasticsearch migration path documented (optional spike)

### Exit Criteria

- Production deployment on K8s
- Load test passes: 1000 RPS, p99 < 500ms
- Security audit findings resolved
- Mobile app can consume Property API
- 1M property seed data searchable < 200ms

---

## Post-Launch Roadmap (Phase 7+)

| Feature | Priority | Dependency |
|---------|----------|------------|
| Elasticsearch search index | High | Phase 5 events |
| Kafka migration (dual-write) | Medium | Phase 5 events |
| OCR property registration | Medium | Phase 4 import |
| Voice input registration | Low | Identity Service |
| GraphQL API (optional) | Low | Phase 2 CRUD |
| Multi-region deployment | Medium | Phase 6 K8s |
| Property comparison API | Low | Phase 3 search |
| Webhook subscriptions (partner) | Medium | Phase 5 events |
| Data export (GDPR/KVKK) | High | Phase 6 enterprise |
| Property aliases / merge UI | Medium | Phase 6 merge |

---

## Risk Register

| Risk | Impact | Mitigation |
|------|--------|------------|
| PostGIS performance at 1M+ rows | High | Denormalized search columns, read replicas, ES in Phase 7 |
| Listing adapter breakage (HTML changes) | Medium | Adapter per provider, monitoring, graceful degradation |
| JWT issuer not ready | Medium | Mock JWT for dev; shared issuer with finward-api |
| Geocoding rate limits | Low | Queue-based, backoff, cache geocoding results |
| Schema evolution complexity | Medium | JSONB metadata, lookup tables, versioned events |
| Team unfamiliar with DDD | Medium | Phase 1 focuses on patterns; code review checklist |

---

## Team Allocation (Suggested)

| Role | Phase 1-2 | Phase 3-4 | Phase 5-6 |
|------|-----------|-----------|-----------|
| Backend Lead | Architecture + domain | Search + geo | Events + production |
| Backend Engineer 1 | CRUD + API | Media + import | Integration |
| Backend Engineer 2 | Infra + DB | Celery + storage | Enterprise + K8s |
| QA Engineer | Test framework | API + integration tests | Load + security tests |
| DevOps | Docker Compose | CI/CD pipeline | K8s + monitoring |

---

## Definition of Done (Per Phase)

1. All deliverables implemented and code-reviewed
2. Unit tests pass (> 85% coverage on new code)
3. Integration tests pass
4. OpenAPI spec updated
5. Architecture docs updated if design changed
6. Deployed to staging and smoke-tested
7. No P0/P1 bugs open
8. Performance benchmarks met (where applicable)

---

## Approval Gate

After reviewing this design package, confirm:

1. **Phase prioritization** — is CRUD before search the right order?
2. **Multi-tenancy model** — shared DB with tenant_id vs schema-per-tenant?
3. **Search Phase 1** — PostgreSQL FTS + PostGIS sufficient, or early Elasticsearch?
4. **Auth integration** — shared JWT with finward-api or dedicated Identity Service?
5. **First listing provider** — sahibinden confirmed?
6. **Object storage** — S3 (prod) + MinIO (dev) acceptable?

**On approval → begin Phase 1 implementation.**
