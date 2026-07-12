from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ExternalDependency:
    name: str
    required: bool
    fallback: str | None = None


EXTERNAL_DEPENDENCIES: tuple[ExternalDependency, ...] = (
    ExternalDependency("postgresql", required=True, fallback=None),
    ExternalDependency("redis", required=True, fallback="degraded: no cache, rate limit, idempotency"),
    ExternalDependency("rabbitmq", required=False, fallback="API works; events queue in outbox only"),
    ExternalDependency("s3", required=False, fallback="media upload endpoints return 503"),
    ExternalDependency("identity_jwks", required=True, fallback="cached keys (1h); stale keys on outage"),
    ExternalDependency("geocoding", required=False, fallback="properties created without coordinates"),
)

# Property Service never calls downstream valuation, risk, or AI services.
FORBIDDEN_OUTBOUND_SERVICES: frozenset[str] = frozenset(
    {"valuation-service", "risk-service", "ai-service", "notification-service"}
)
