# Downstream Event Consumers

Property Service publishes domain events via the transactional outbox → RabbitMQ (`property.events` exchange) using [CloudEvents 1.0](https://cloudevents.io/) envelopes.

## Subscribing

1. Bind a durable queue to the `property.events` topic exchange.
2. Filter by routing keys (e.g. `property.created.v1`, `property.price_changed.v1`).
3. Parse the CloudEvents envelope; business payload is in `data`.
4. Use `tenantid` and `correlationid` extensions for multi-tenant tracing.

## Event Catalog

See [06-event-definitions.md](../architecture/06-event-definitions.md) for the full event catalog and versioning policy.

| Event | Routing Key | Typical Consumers |
|-------|-------------|-----------------|
| PropertyCreated | `property.created.v1` | Search indexer, Notification |
| PropertyUpdated | `property.updated.v1` | Search indexer |
| PropertyPriceChanged | `property.price_changed.v1` | Valuation Service |
| PropertyLocationChanged | `property.location_changed.v1` | Risk Service |
| PropertyStatusChanged | `property.status_changed.v1` | Notification Service |
| PropertyDeleted | `property.deleted.v1` | Search indexer |

## Guarantees

- **At-least-once** delivery via outbox retry with exponential backoff.
- Events are emitted **after** the database transaction commits.
- After 5 publish failures, events move to the dead-letter exchange for manual review.

## Property Service Boundaries

Property Service **never calls** Valuation, Risk, or Notification services. Integration is **event-only** (or read API for portfolio references).

## Local Development

```bash
docker compose -f docker/docker-compose.yml up -d rabbitmq
# RabbitMQ management UI: http://localhost:15672 (property / property)
```

Outbox processing runs via Celery beat (`property.outbox.publish` every 5 seconds).
