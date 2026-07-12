# 13. Cache Strategy

## Overview

Redis cache-aside pattern with event-driven invalidation. Cache is **never** the source of truth — PostgreSQL remains SSOT.

```
Read Request
    │
    ▼
Check Redis Cache ──hit──► Return cached data
    │
   miss
    │
    ▼
Query PostgreSQL
    │
    ▼
Store in Redis (with TTL)
    │
    ▼
Return data

Write Request
    │
    ▼
Update PostgreSQL (transaction)
    │
    ▼
Publish domain event
    │
    ▼
Cache invalidation handler
```

---

## Cache Key Design

| Key Pattern | Data | TTL | Invalidation Trigger |
|-------------|------|-----|---------------------|
| `property:detail:{property_id}` | Full property JSON | 15 min | PropertyUpdated, PropertyDeleted, PropertyStatusChanged, PropertyImagesUpdated, PropertyDocumentsUpdated |
| `property:code:{tenant_id}:{code}` | Property ID | 30 min | PropertyDeleted |
| `property:slug:{tenant_id}:{slug}` | Property ID | 30 min | PropertyUpdated (slug change) |
| `property:search:{tenant_id}:{hash}` | Search results page | 5 min | Any property mutation in tenant |
| `property:nearby:{tenant_id}:{geohash}:{radius}` | Nearby results | 5 min | PropertyLocationChanged in area |
| `property:stats:{tenant_id}` | Statistics aggregate | 30 min | Any property mutation in tenant |
| `property:metadata:{property_id}` | Metadata JSONB | 15 min | PropertyUpdated (metadata) |
| `property:types` | Lookup table | 24 hours | Admin update to lookup |
| `property:amenities` | Lookup table | 24 hours | Admin update to lookup |
| `idempotency:{key}` | Response body | 24 hours | TTL expiry |
| `ratelimit:{client_id}` | Request counter | 60 sec | TTL expiry |
| `jwks:keys` | JWT public keys | 1 hour | Key rotation event |

### Search Cache Key Hash

```python
def search_cache_key(tenant_id: UUID, criteria: PropertySearchCriteria) -> str:
    payload = criteria.model_dump_json(exclude_none=True, sort_keys=True)
    hash_digest = hashlib.sha256(payload.encode()).hexdigest()[:16]
    return f"property:search:{tenant_id}:{hash_digest}"
```

---

## Cache-Aside Implementation

```python
class RedisPropertyCache(IPropertyCache):

    async def get_property(self, property_id: UUID) -> dict | None:
        key = f"property:detail:{property_id}"
        data = await self.redis.get(key)
        return json.loads(data) if data else None

    async def set_property(self, property_id: UUID, data: dict, ttl: int = 900) -> None:
        key = f"property:detail:{property_id}"
        await self.redis.setex(key, ttl, json.dumps(data, default=str))

    async def invalidate_property(self, property_id: UUID) -> None:
        keys = [
            f"property:detail:{property_id}",
            f"property:metadata:{property_id}",
        ]
        await self.redis.delete(*keys)
```

---

## Invalidation Strategy

### Event-Driven Invalidation

| Event | Invalidation Actions |
|-------|---------------------|
| `PropertyCreated` | Invalidate `property:stats:{tenant_id}` |
| `PropertyUpdated` | Invalidate `property:detail:{id}`, `property:slug:*`, `property:stats:{tenant_id}`, tenant search cache |
| `PropertyDeleted` | Invalidate detail, code, slug, stats, search |
| `PropertyPriceChanged` | Invalidate detail, search (price-sensitive queries) |
| `PropertyLocationChanged` | Invalidate detail, nearby caches in geohash neighborhood |
| `PropertyStatusChanged` | Invalidate detail, search, stats |
| `PropertyImagesUpdated` | Invalidate detail (primary_image_url in search) |
| `PropertyDocumentsUpdated` | Invalidate detail |

### Tenant Search Cache Invalidation

On any property mutation, invalidate all search keys for the tenant:

```python
async def invalidate_tenant_search(self, tenant_id: UUID) -> None:
    pattern = f"property:search:{tenant_id}:*"
    cursor = 0
    while True:
        cursor, keys = await self.redis.scan(cursor, match=pattern, count=100)
        if keys:
            await self.redis.delete(*keys)
        if cursor == 0:
            break
```

**Phase 2 optimization:** Track search cache keys in a Redis SET per tenant instead of SCAN.

### Nearby Cache Invalidation

On `PropertyLocationChanged`, invalidate geohash neighbors (9-cell grid):

```python
def invalidate_nearby(geohash: str, tenant_id: UUID):
    for neighbor in geohash_neighbors(geohash):
        pattern = f"property:nearby:{tenant_id}:{neighbor}:*"
        # delete matching keys
```

---

## Cache Warming

| Scenario | Strategy |
|----------|----------|
| Popular properties | Warm on first access; extend TTL on repeated hits (adaptive) |
| Statistics | Pre-compute via Celery beat every 30 min for active tenants |
| Lookup tables | Load on startup; 24h TTL with background refresh |

---

## Cache Stampede Prevention

For high-traffic property detail reads:

```python
async def get_property_cached(property_id: UUID) -> dict:
    cached = await cache.get_property(property_id)
    if cached:
        return cached

  # Distributed lock
    lock_key = f"lock:property:detail:{property_id}"
    acquired = await redis.set(lock_key, "1", nx=True, ex=5)
    if not acquired:
        await asyncio.sleep(0.1)
        return await cache.get_property(property_id)  # retry

    try:
        data = await repository.get_by_id(property_id)
        await cache.set_property(property_id, data)
        return data
    finally:
        await redis.delete(lock_key)
```

---

## Redis Configuration

| Setting | Value |
|---------|-------|
| Max memory | 2 GB (dev), 8 GB+ (prod) |
| Eviction policy | `allkeys-lru` |
| Persistence | RDB snapshots (cache data is disposable) |
| Connection pool | 20 connections per API instance |
| Serialization | JSON (human-readable, debuggable) |

---

## What NOT to Cache

| Data | Reason |
|------|--------|
| Audit logs | Must always be fresh |
| Outbox events | Transactional integrity |
| Write operations | Never cache mutations |
| User-specific ownership details (partner API) | Per-user authorization |
| Bulk job status | Short-lived, polled frequently |

---

## Monitoring

| Metric | Alert Threshold |
|--------|----------------|
| `cache_hit_ratio` | < 70% for property:detail |
| `cache_memory_usage` | > 80% maxmemory |
| `cache_invalidation_rate` | Spike > 3x baseline |
| `cache_latency_p99` | > 5ms |
