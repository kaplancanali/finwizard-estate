from __future__ import annotations

# Retry policy reference (docs/architecture/11-error-handling-strategy.md).
RETRY_POLICIES: dict[str, dict[str, object]] = {
    "postgresql": {"retries": 3, "strategy": "connection_pool"},
    "redis": {"retries": 2, "backoff_ms": 50, "fallback": "skip_cache"},
    "rabbitmq": {"retries": 3, "context": "outbox_processor"},
    "geocoding": {"retries": 2, "strategy": "exponential_backoff", "circuit_breaker": "5_failures_60s"},
    "object_storage": {"retries": 3, "strategy": "boto_builtin"},
}
