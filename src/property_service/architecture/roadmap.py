from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class PhaseStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETE = "complete"


class DeliverableStatus(str, Enum):
    PENDING = "pending"
    PARTIAL = "partial"
    COMPLETE = "complete"


@dataclass(frozen=True)
class RoadmapPhase:
    number: int
    name: str
    weeks: str
    goal: str
    exit_criteria: tuple[str, ...]


@dataclass
class RoadmapDeliverable:
    id: str
    phase: int
    title: str
    artifact_checks: tuple[str, ...] = ()
    source_checks: tuple[str, ...] = ()
    test_globs: tuple[str, ...] = ()
    notes: str | None = None


@dataclass
class RiskItem:
    risk: str
    impact: str
    mitigation: str


@dataclass
class PostLaunchItem:
    feature: str
    priority: str
    dependency: str


@dataclass
class ApprovalGate:
    question: str
    recommendation: str


ROADMAP_PHASES: tuple[RoadmapPhase, ...] = (
    RoadmapPhase(
        1,
        "Foundation",
        "Weeks 1–4",
        "Project scaffold, domain model, database, basic API skeleton.",
        (
            "docker compose up starts all services",
            "Migrations run successfully",
            "Health checks pass",
            "Domain unit tests > 90% coverage",
            "CI pipeline: lint + unit tests",
        ),
    ),
    RoadmapPhase(
        2,
        "Core CRUD",
        "Weeks 5–8",
        "Full property lifecycle — create, read, update, delete, status management.",
        (
            "Full CRUD via API with JWT auth",
            "Audit trail verifiable",
            "Optimistic locking tested (409 on conflict)",
            "Status state machine fully tested",
            "API integration tests > 80% endpoint coverage",
        ),
    ),
    RoadmapPhase(
        3,
        "Search",
        "Weeks 9–12",
        "Powerful property search with geo, filters, pagination, caching.",
        (
            "All search filter types working",
            "Geo search accurate within 1% of PostGIS reference",
            "Cache hit ratio > 70% in load test",
            "Search performance benchmarks documented",
        ),
    ),
    RoadmapPhase(
        4,
        "Media & Import",
        "Weeks 13–16",
        "Image/document management, bulk import, external source registration.",
        (
            "End-to-end image upload and thumbnail generation",
            "Bulk import of 500 properties completes < 10 min",
            "Listing URL import creates valid property",
            "Geocoding populates coordinates from address",
        ),
    ),
    RoadmapPhase(
        5,
        "Events & Integration",
        "Weeks 17–20",
        "Event-driven architecture, outbox, downstream consumer readiness.",
        (
            "Events published reliably (outbox → RabbitMQ)",
            "Zero event loss in chaos test",
            "Downstream consumer can subscribe and process events",
            "Rate limiting enforced per tier",
            "Distributed tracing visible in Jaeger",
        ),
    ),
    RoadmapPhase(
        6,
        "Enterprise & Production",
        "Weeks 21–24",
        "Production hardening, enterprise features, scale validation.",
        (
            "Production deployment on K8s",
            "Load test passes: 1000 RPS, p99 < 500ms",
            "Security audit findings resolved",
            "Mobile app can consume Property API",
            "1M property seed data searchable < 200ms",
        ),
    ),
)

DELIVERABLES: tuple[RoadmapDeliverable, ...] = (
    # Phase 1
    RoadmapDeliverable("p1-scaffold", 1, "Project scaffold", ("pyproject.toml", "docker/docker-compose.yml", "Makefile")),
    RoadmapDeliverable("p1-config", 1, "Configuration & logging", ("src/property_service/config/settings.py", "src/property_service/config/logging.py")),
    RoadmapDeliverable("p1-migrations", 1, "PostgreSQL schema + Alembic", ("alembic.ini", "migrations/versions/001_initial_schema.py")),
    RoadmapDeliverable("p1-domain", 1, "Domain model", ("src/property_service/domain/aggregates/property.py",)),
    RoadmapDeliverable("p1-repos", 1, "Repository interfaces + SQLAlchemy", ("src/property_service/domain/repositories/property_repository.py", "src/property_service/infrastructure/persistence/repositories/property_repository.py")),
    RoadmapDeliverable("p1-uow", 1, "Unit of Work", ("src/property_service/application/unit_of_work.py", "src/property_service/infrastructure/persistence/unit_of_work.py")),
    RoadmapDeliverable("p1-di", 1, "DI container", ("src/property_service/di/container.py",)),
    RoadmapDeliverable("p1-health", 1, "Health endpoints", source_checks=('"/health"', '"/health/ready"', '"/health/startup"')),
    RoadmapDeliverable("p1-auth", 1, "JWT middleware", ("src/property_service/presentation/middleware/authentication.py",)),
    RoadmapDeliverable("p1-errors", 1, "Exception handlers", ("src/property_service/presentation/exception_handlers.py",)),
    RoadmapDeliverable("p1-domain-tests", 1, "Domain unit tests", test_globs=("tests/unit/domain/test_*.py",)),
    # Phase 2
    RoadmapDeliverable("p2-create", 2, "POST /properties", source_checks=('post("",',)),
    RoadmapDeliverable("p2-read", 2, "GET property by id/code/slug", source_checks=('"/{property_id}"', '"/code/{property_code}"', '"/slug/{slug}"')),
    RoadmapDeliverable("p2-update", 2, "PUT/PATCH property", source_checks=('put("/{property_id}"', 'patch("/{property_id}"')),
    RoadmapDeliverable("p2-delete-restore", 2, "DELETE + restore", source_checks=('delete("/{property_id}"', '/restore')),
    RoadmapDeliverable("p2-status", 2, "Status state machine", source_checks=('/status',), test_globs=("tests/unit/domain/test_validator_and_specs.py",)),
    RoadmapDeliverable("p2-register", 2, "POST /register", source_checks=('"/register"',)),
    RoadmapDeliverable("p2-lookups", 2, "Lookup endpoints", source_checks=('"/property-types"', '"/statuses"')),
    RoadmapDeliverable("p2-openapi", 2, "OpenAPI generation", ("scripts/generate_openapi.py",)),
    RoadmapDeliverable("p2-integration", 2, "Integration tests", test_globs=("tests/integration/api/test_*.py",)),
    # Phase 3
    RoadmapDeliverable("p3-search", 3, "Search endpoints", source_checks=('"/search"', '"/nearby"', '"/map"')),
    RoadmapDeliverable("p3-statistics", 3, "Statistics", source_checks=('"/statistics"',)),
    RoadmapDeliverable("p3-cache", 3, "Redis search caching", ("src/property_service/infrastructure/cache/property_cache_manager.py", "tests/unit/infrastructure/test_cache_strategy.py")),
    RoadmapDeliverable("p3-perf", 3, "Search performance tests", ("tests/performance/test_search_benchmark.py",), notes="Benchmark scaffold present; enable for 1M load validation"),
    # Phase 4
    RoadmapDeliverable("p4-storage", 4, "S3/MinIO integration", ("src/property_service/infrastructure/storage/s3_storage.py", "docker/docker-compose.yml")),
    RoadmapDeliverable("p4-images", 4, "Image upload flow", source_checks=('/images', '/confirm')),
    RoadmapDeliverable("p4-documents", 4, "Document management", source_checks=('/documents',)),
    RoadmapDeliverable("p4-bulk", 4, "Bulk operations", source_checks=('post("/import"', '"/jobs/{job_id}"')),
    RoadmapDeliverable("p4-celery", 4, "Celery workers", ("src/property_service/infrastructure/celery/app.py", "docker/Dockerfile.worker")),
    RoadmapDeliverable("p4-geocoding", 4, "Geocoding tasks", ("src/property_service/infrastructure/celery/tasks/geocoding_tasks.py",)),
    RoadmapDeliverable("p4-idempotency", 4, "Idempotency middleware", ("src/property_service/presentation/middleware/idempotency.py",)),
    RoadmapDeliverable("p4-listing", 4, "Listing URL import", ("src/property_service/infrastructure/listing/listing_adapter.py",), notes="Stub adapter; sahibinden provider pending"),
    # Phase 5
    RoadmapDeliverable("p5-events", 5, "Domain events + outbox", ("src/property_service/infrastructure/messaging/outbox_processor.py", "src/property_service/infrastructure/celery/tasks/outbox_tasks.py")),
    RoadmapDeliverable("p5-cloudevents", 5, "CloudEvents publisher", ("src/property_service/infrastructure/messaging/cloudevents.py",)),
    RoadmapDeliverable("p5-history", 5, "History endpoints", source_checks=('/history/price', '/history/status')),
    RoadmapDeliverable("p5-versions", 5, "Version + audit endpoints", source_checks=('/versions', '/audit-logs')),
    RoadmapDeliverable("p5-metadata", 5, "Metadata endpoints", source_checks=('/metadata',)),
    RoadmapDeliverable("p5-rate-limit", 5, "Rate limiting", ("src/property_service/presentation/middleware/rate_limiting.py",)),
    RoadmapDeliverable("p5-api-keys", 5, "API key authentication", ("src/property_service/application/security/api_keys.py",)),
    RoadmapDeliverable("p5-metrics", 5, "Prometheus metrics", source_checks=('"/metrics"',)),
    RoadmapDeliverable("p5-tracing", 5, "OpenTelemetry tracing", notes="Dependencies declared; instrumentation wiring pending"),
    RoadmapDeliverable("p5-consumer-docs", 5, "Consumer documentation", ("docs/consumers/README.md",)),
    # Phase 6
    RoadmapDeliverable("p6-rbac", 6, "RBAC implementation", ("src/property_service/config/rbac.py", "tests/unit/application/test_security_strategy.py")),
    RoadmapDeliverable("p6-helm", 6, "Kubernetes Helm chart", ("deploy/helm/property-service/Chart.yaml",)),
    RoadmapDeliverable("p6-prod-compose", 6, "Production Docker Compose", ("docker/docker-compose.prod.yml",)),
    RoadmapDeliverable("p6-ci", 6, "CI/CD pipeline", (".github/workflows/ci.yml",)),
    RoadmapDeliverable("p6-merge", 6, "Property merge service", ("src/property_service/domain/services/property_merge_service.py",), notes="Domain stub; merge API pending"),
    RoadmapDeliverable("p6-read-replica", 6, "Read replica support", notes="Not implemented"),
    RoadmapDeliverable("p6-partitioning", 6, "Audit log partitioning", notes="Not implemented"),
    RoadmapDeliverable("p6-load-test", 6, "Load testing at scale", notes="Performance benchmark scaffold only"),
    RoadmapDeliverable("p6-sdk", 6, "SDK generation path", ("scripts/generate_openapi.py",), notes="OpenAPI export ready; TS/Dart codegen pending"),
    RoadmapDeliverable("p6-finward-api", 6, "finward-api integration", notes="property_id linkage pending"),
)

RISK_REGISTER: tuple[RiskItem, ...] = (
    RiskItem("PostGIS performance at 1M+ rows", "High", "Denormalized search columns, read replicas, ES in Phase 7"),
    RiskItem("Listing adapter breakage (HTML changes)", "Medium", "Adapter per provider, monitoring, graceful degradation"),
    RiskItem("JWT issuer not ready", "Medium", "Mock JWT for dev; shared issuer with finward-api"),
    RiskItem("Geocoding rate limits", "Low", "Queue-based, backoff, cache geocoding results"),
    RiskItem("Schema evolution complexity", "Medium", "JSONB metadata, lookup tables, versioned events"),
    RiskItem("Team unfamiliar with DDD", "Medium", "Phase 1 focuses on patterns; code review checklist"),
)

POST_LAUNCH_ITEMS: tuple[PostLaunchItem, ...] = (
    PostLaunchItem("Elasticsearch search index", "High", "Phase 5 events"),
    PostLaunchItem("Kafka migration (dual-write)", "Medium", "Phase 5 events"),
    PostLaunchItem("OCR property registration", "Medium", "Phase 4 import"),
    PostLaunchItem("Voice input registration", "Low", "Identity Service"),
    PostLaunchItem("GraphQL API (optional)", "Low", "Phase 2 CRUD"),
    PostLaunchItem("Multi-region deployment", "Medium", "Phase 6 K8s"),
    PostLaunchItem("Property comparison API", "Low", "Phase 3 search"),
    PostLaunchItem("Webhook subscriptions (partner)", "Medium", "Phase 5 events"),
    PostLaunchItem("Data export (GDPR/KVKK)", "High", "Phase 6 enterprise"),
    PostLaunchItem("Property aliases / merge UI", "Medium", "Phase 6 merge"),
)

APPROVAL_GATES: tuple[ApprovalGate, ...] = (
    ApprovalGate("Phase prioritization", "CRUD before search is correct for SSOT validation"),
    ApprovalGate("Multi-tenancy model", "Shared DB with tenant_id (schema-per-tenant optional in Phase 6)"),
    ApprovalGate("Search Phase 1", "PostgreSQL FTS + PostGIS sufficient; Elasticsearch deferred to Phase 7"),
    ApprovalGate("Auth integration", "Shared JWT with finward-api via JWKS"),
    ApprovalGate("First listing provider", "sahibinden as first adapter target"),
    ApprovalGate("Object storage", "S3 (prod) + MinIO (dev)"),
)

DEFINITION_OF_DONE: tuple[str, ...] = (
    "All deliverables implemented and code-reviewed",
    "Unit tests pass (> 85% coverage on new code)",
    "Integration tests pass",
    "OpenAPI spec updated",
    "Architecture docs updated if design changed",
    "Deployed to staging and smoke-tested",
    "No P0/P1 bugs open",
    "Performance benchmarks met (where applicable)",
)
