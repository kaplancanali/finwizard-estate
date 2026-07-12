# Deployment

Kubernetes and CI/CD assets for the Property Service, aligned with [15-deployment-strategy.md](../docs/architecture/15-deployment-strategy.md).

## Environments

| Environment | Helm values file | Trigger |
|-------------|------------------|---------|
| `local` | — | `docker compose -f docker/docker-compose.yml up` |
| `dev` | `values-dev.yaml` | Auto on push to `main` |
| `staging` | `values-staging.yaml` | Manual approval |
| `production` | `values-production.yaml` | Manual approval + canary |

## Helm

```bash
# Dev (single replica, no ingress)
helm upgrade --install property-service deploy/helm/property-service \
  -f deploy/helm/property-service/values-dev.yaml \
  --set secrets.databaseUrl="$DATABASE_URL" \
  --set secrets.redisUrl="$REDIS_URL" \
  --set secrets.rabbitmqUrl="$RABBITMQ_URL" \
  --set secrets.jwtSecret="$JWT_SECRET"

# Production
helm upgrade --install property-service deploy/helm/property-service \
  -f deploy/helm/property-service/values-production.yaml \
  --set image.tag="$GIT_SHA"
```

## Health probes

| Endpoint | Probe | Purpose |
|----------|-------|---------|
| `GET /health` | Liveness | Process alive |
| `GET /health/ready` | Readiness | DB + Redis + RabbitMQ |
| `GET /health/startup` | Startup | Migrations complete, lookups seeded |

## CI/CD

GitHub Actions workflow (`.github/workflows/ci.yml`):

1. Lint (ruff)
2. Unit tests
3. Integration tests
4. Docker image build
5. Deploy dev → staging → production (gated)

## Zero-downtime rollout

API deployment uses `maxUnavailable: 0`, `maxSurge: 1`, readiness probe gating, and a 15s `preStop` drain hook. Database migrations run as a Helm pre-install/pre-upgrade Job.
