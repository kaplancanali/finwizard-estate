# FINWARD Property Service — Architecture Design

> **Status:** Design Phase — Pending approval before implementation  
> **Version:** 1.0.0-draft  
> **Last Updated:** 2026-06-30

## Purpose

The **Property Service** is the central domain service and **Single Source of Truth (SSOT)** for all real estate asset data within the FINWARD Intelligence Platform. It powers the Mobile App, Web Platform, Admin Dashboard, Enterprise API, and Partner API.

This is **not** a CRUD microservice. It is an enterprise-grade, event-driven, CQRS-ready domain service designed to scale to millions of properties and enterprise tenants.

## Explicit Non-Responsibilities

The Property Service **must never** contain:

| Excluded Domain | Owner Service |
|-----------------|---------------|
| Investment Analysis | Investment Analysis Service |
| Earthquake Analysis | Risk / Geospatial Service |
| Photo AI / Street AI / Satellite AI | Vision AI Services |
| Recommendation Engine | Recommendation Service |
| Risk Engine | Risk Service |
| Market Analysis | Market Intelligence Service |
| Price / Rental / Future Value Prediction | Valuation / ML Services |

## Technology Stack

| Layer | Technology |
|-------|------------|
| Runtime | Python 3.13 |
| API | FastAPI + OpenAPI 3.1 |
| ORM | SQLAlchemy 2.0 (async) |
| Migrations | Alembic |
| Database | PostgreSQL 16 + PostGIS |
| Cache | Redis 7 |
| Message Broker | RabbitMQ |
| Background Jobs | Celery |
| Auth | JWT (platform-issued) |
| Validation | Pydantic v2 |
| Containerization | Docker / Docker Compose |

## Design Documents Index

| # | Document | Description |
|---|----------|-------------|
| 1 | [Domain Model](./01-domain-model.md) | Aggregates, entities, value objects, domain events |
| 2 | [Folder Structure](./02-folder-structure.md) | Clean Architecture + DDD package layout |
| 3 | [Database Design](./03-database-design.md) | Normalized schema, indexes, partitioning strategy |
| 4 | [Entity Relationship Diagram](./04-entity-relationship-diagram.md) | ERD with Mermaid diagrams |
| 5 | [API Contract](./05-api-contract.md) | REST endpoints, request/response schemas |
| 6 | [Event Definitions](./06-event-definitions.md) | Domain events, outbox, future Kafka |
| 7 | [Service Responsibilities](./07-service-responsibilities.md) | Application & domain service boundaries |
| 8 | [Repository Interfaces](./08-repository-interfaces.md) | Persistence abstractions |
| 9 | [DTO Design](./09-dto-design.md) | Pydantic schemas by layer |
| 10 | [Validation Rules](./10-validation-rules.md) | Business & input validation |
| 11 | [Error Handling Strategy](./11-error-handling-strategy.md) | Error taxonomy, HTTP mapping |
| 12 | [Security Strategy](./12-security-strategy.md) | RBAC, JWT, API keys, audit |
| 13 | [Cache Strategy](./13-cache-strategy.md) | Redis keys, TTL, invalidation |
| 14 | [Background Jobs](./14-background-jobs.md) | Celery tasks & queues |
| 15 | [Deployment Strategy](./15-deployment-strategy.md) | K8s, scaling, environments |
| 16 | [Docker Structure](./16-docker-structure.md) | Container layout & compose |
| 17 | [Dependency Graph](./17-dependency-graph.md) | Module & runtime dependencies |
| 18 | [Development Roadmap](./18-development-roadmap.md) | Phased implementation plan |

## Architecture Overview

```
### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           FINWARD Platform Clients                          │
│  Mobile App │ Web Platform │ Admin Dashboard │ Enterprise API │ Partner API │
└──────────────────────────────────┬──────────────────────────────────────────┘
                                   │ HTTPS / JWT
                                   ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                         API Gateway / Load Balancer                         │
└──────────────────────────────────┬──────────────────────────────────────────┘
                                   │
                                   ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                          PROPERTY SERVICE (FastAPI)                         │
│  ┌─────────────┐  ┌──────────────┐  ┌─────────────┐  ┌──────────────────┐  │
│  │ Presentation│  │ Application  │  │   Domain    │  │  Infrastructure  │  │
│  │  (Routes)   │→ │  (Use Cases) │→ │ (Aggregates)│← │ (Repos, Cache)   │  │
│  └─────────────┘  └──────────────┘  └─────────────┘  └──────────────────┘  │
└───────┬─────────────────┬──────────────────┬─────────────────┬──────────────┘
        │                 │                  │                 │
        ▼                 ▼                  ▼                 ▼
   PostgreSQL          Redis             RabbitMQ         Object Storage
   + PostGIS                              (Events)         (S3/MinIO)
        ▲                 ▲                  ▲
        │                 │                  │
   ┌────┴─────────────────┴──────────────────┴──────────────────────────────┐
   │                        Celery Workers                                   │
   │  Geocoding │ Image Processing │ Import Jobs │ External Sync │ Outbox    │
   └─────────────────────────────────────────────────────────────────────────┘
                                   │
                                   ▼
                    Downstream Consumers (Future Kafka)
                    Valuation │ Risk │ Search Index │ Analytics
```

### Core Principles

1. **Domain-Driven Design** — Property aggregate as SSOT; bounded context isolation
2. **Clean Architecture** — Dependencies point inward; domain has zero infrastructure imports
3. **CQRS-Ready** — Separate write model (normalized PG) and read model (search projection)
4. **Event-Driven** — Outbox pattern → RabbitMQ → future Kafka migration path
5. **Multi-Tenancy** — Tenant-scoped data with row-level security option
6. **Optimistic Concurrency** — Version column on aggregate root
7. **Soft Delete** — `deleted_at` with audit trail preservation
8. **Extensibility** — Lookup tables + JSONB metadata for future property types and sources

## Approval Checklist

Before implementation begins, confirm:

- [ ] Domain model and aggregate boundaries
- [ ] Database schema and indexing strategy
- [ ] API contract (versioning, bulk ops, idempotency)
- [ ] Event schema and outbox strategy
- [ ] Multi-tenancy model (shared DB vs schema-per-tenant)
- [ ] Object storage provider (S3 / MinIO / GCS)
- [ ] Search strategy for Phase 1 (PostgreSQL FTS + PostGIS vs early Elasticsearch)
- [ ] Auth integration (shared JWT issuer with finward-api)
- [ ] Development roadmap phasing
