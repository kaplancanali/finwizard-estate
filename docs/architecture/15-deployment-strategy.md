# 15. Deployment Strategy

## Environments

| Environment | Purpose | Infrastructure |
|-------------|---------|---------------|
| `local` | Developer machines | Docker Compose |
| `dev` | Integration testing | K8s (single node) / Compose |
| `staging` | Pre-production validation | K8s (multi-node) |
| `production` | Live traffic | K8s (multi-AZ, auto-scaling) |

---

## Kubernetes Architecture (Production)

```
┌─────────────────────────────────────────────────────────────────┐
│                        Ingress (NGINX / ALB)                    │
│                   TLS termination, rate limiting                │
└────────────────────────────┬────────────────────────────────────┘
                             │
              ┌──────────────┼──────────────┐
              ▼              ▼              ▼
     ┌─────────────┐  ┌─────────────┐  ┌─────────────┐
     │ API Pod x3  │  │ API Pod x3  │  │ API Pod x3  │
     │ (HPA 3-20)  │  │             │  │             │
     └──────┬──────┘  └──────┬──────┘  └──────┬──────┘
            │                │                │
     ┌──────┴────────────────┴────────────────┴──────┐
     │                                                │
     ▼              ▼              ▼                 ▼
┌─────────┐  ┌──────────┐  ┌──────────┐    ┌──────────────┐
│PostgreSQL│  │  Redis   │  │ RabbitMQ │    │ Worker Pods  │
│ (RDS)   │  │(ElastiC.)│  │ (Amazon  │    │ x2-10 (HPA)  │
│+ PostGIS│  │          │  │   MQ)    │    │ Celery       │
└─────────┘  └──────────┘  └──────────┘    └──────────────┘
                                                  │
                                                  ▼
                                           ┌──────────────┐
                                           │ S3 / MinIO   │
                                           │ (media)      │
                                           └──────────────┘
```

---

## Service Components

| Component | Replicas | Scaling Trigger |
|-----------|----------|-----------------|
| API (FastAPI) | 3–20 | CPU > 70% or RPS > 500/pod |
| Celery Worker (default) | 2–10 | Queue depth > 100 |
| Celery Worker (image) | 1–5 | Queue depth > 20 |
| Celery Worker (import) | 1–3 | Queue depth > 5 |
| Celery Beat | 1 (singleton) | — |
| Outbox Processor | 2 | Queue depth > 50 |

---

## Resource Limits

### API Pod

```yaml
resources:
  requests:
    cpu: 500m
    memory: 512Mi
  limits:
    cpu: 2000m
    memory: 1Gi
```

### Worker Pod (image processing)

```yaml
resources:
  requests:
    cpu: 1000m
    memory: 1Gi
  limits:
    cpu: 2000m
    memory: 2Gi
```

---

## Database

| Setting | Dev | Production |
|---------|-----|------------|
| Instance | PostgreSQL 16 + PostGIS | RDS PostgreSQL 16 Multi-AZ |
| Storage | 20 GB SSD | 500 GB–2 TB gp3 |
| Connections | 50 | PgBouncer (500 pool) |
| Backups | Daily | Continuous + daily snapshots (35 day retention) |
| Read replicas | 0 | 1–2 for search queries (Phase 2) |

### Migration Strategy

1. Alembic migrations run as K8s Job before deployment
2. Backward-compatible migrations only (expand → deploy → contract)
3. Rollback: previous image tag + reverse migration if needed

---

## CI/CD Pipeline

```
Push to main
    │
    ▼
┌─────────────┐
│   Lint      │  ruff, mypy
└──────┬──────┘
       ▼
┌─────────────┐
│  Unit Tests │  pytest (domain + application)
└──────┬──────┘
       ▼
┌─────────────┐
│ Integration │  pytest + testcontainers (PG, Redis, RabbitMQ)
└──────┬──────┘
       ▼
┌─────────────┐
│ Build Image │  Docker multi-stage build
└──────┬──────┘
       ▼
┌─────────────┐
│ Push to ECR │  Tag: git SHA + semver
└──────┬──────┘
       ▼
┌─────────────┐
│ Deploy Dev  │  Auto
└──────┬──────┘
       ▼
┌─────────────┐
│ Deploy Stg  │  Manual approval
└──────┬──────┘
       ▼
┌─────────────┐
│ Deploy Prod │  Manual approval + canary (10% → 50% → 100%)
└─────────────┘
```

---

## Health Checks

| Endpoint | K8s Probe | Criteria |
|----------|-----------|----------|
| `GET /health` | Liveness | Process alive |
| `GET /health/ready` | Readiness | DB + Redis + RabbitMQ connected |
| `GET /health/startup` | Startup | Migrations complete, lookups seeded |

---

## Observability Stack

| Concern | Tool |
|---------|------|
| Logging | Structured JSON → Fluentd → Elasticsearch/Loki |
| Metrics | Prometheus + Grafana |
| Tracing | OpenTelemetry → Jaeger/Tempo |
| Alerting | Alertmanager → PagerDuty/Slack |
| Dashboards | Grafana (API latency, cache hit ratio, queue depth) |

### Key Alerts

| Alert | Condition |
|-------|-----------|
| API error rate | 5xx > 1% for 5 min |
| API latency | p99 > 2s for 5 min |
| DB connection pool | > 80% utilization |
| Redis memory | > 85% |
| Celery DLQ | > 0 messages |
| Outbox backlog | > 1000 pending events for 10 min |
| Disk usage | > 80% |

---

## Data Residency

| Region | Deployment | Data Location |
|--------|------------|---------------|
| Turkey (primary) | `eu-central-1` or `tr-istanbul` | TR/EU data |
| EU | `eu-west-1` | EU data (GDPR) |

Tenant-level data residency configuration in Phase 3.

---

## Disaster Recovery

| Metric | Target |
|--------|--------|
| RPO (Recovery Point Objective) | 1 hour |
| RTO (Recovery Time Objective) | 4 hours |
| Backup frequency | Continuous WAL + daily snapshots |
| DR drill | Quarterly |

---

## Zero-Downtime Deployment

1. Rolling update with `maxUnavailable: 0`, `maxSurge: 1`
2. Readiness probe must pass before receiving traffic
3. PreStop hook: drain connections (15s grace period)
4. Database migrations: backward-compatible only
5. Feature flags for risky changes (LaunchDarkly / env-based)

---

## Secrets & Config

| Type | Management |
|------|------------|
| Secrets (DB, Redis, MQ, S3) | Kubernetes Secrets + Vault |
| Config (feature flags, rate limits) | ConfigMap |
| Environment-specific | Helm values per environment |

---

## Network Security

| Rule | Implementation |
|------|---------------|
| API → public internet | Ingress only |
| Workers → no public access | Internal only |
| DB/Redis/MQ | Private subnet, security groups |
| S3 | VPC endpoint |
| Inter-service | mTLS via service mesh (Phase 2, Istio) |
