# 14. Background Jobs

## Celery Architecture

```
┌──────────────┐     ┌──────────────┐     ┌──────────────────────┐
│  FastAPI API │────►│   RabbitMQ   │────►│   Celery Workers     │
│  (producer)  │     │   (broker)   │     │   (consumers)        │
└──────────────┘     └──────────────┘     └──────────────────────┘
                            │                        │
                            │                        ▼
                     ┌──────┴───────┐         ┌─────────────┐
                     │ Celery Beat  │         │ PostgreSQL  │
                     │ (scheduler)  │         │ Redis / S3  │
                     └──────────────┘         └─────────────┘
```

---

## Queue Topology

| Queue | Priority | Concurrency | Purpose |
|-------|----------|-------------|---------|
| `property.default` | Normal | 4 | General tasks |
| `property.image` | Normal | 2 | Image processing (CPU-bound) |
| `property.import` | Low | 2 | Bulk import (long-running) |
| `property.geocoding` | Normal | 4 | Geocoding API calls |
| `property.sync` | Low | 2 | External listing sync |
| `property.outbox` | High | 4 | Event publishing |
| `property.maintenance` | Low | 1 | Cleanup, stats refresh |

### Dead Letter Queue

Failed tasks after max retries → `property.dlq` → alert + manual review.

---

## Task Catalog

### Image Processing

#### `property.image.process_upload`

**Trigger:** Image upload confirmed  
**Queue:** `property.image`

```
1. Download original from S3
2. Validate image integrity
3. Generate thumbnails (150px, 400px, 800px)
4. Optimize original (WebP conversion optional)
5. Upload processed versions to S3
6. Update property_images record (urls, dimensions, status=ready)
7. Emit PropertyImagesUpdated event
```

**Retry:** 3x, exponential backoff (30s, 60s, 120s)  
**Timeout:** 120 seconds

#### `property.image.cleanup_orphaned`

**Trigger:** Celery beat (daily 03:00 UTC)  
**Queue:** `property.maintenance`

Remove S3 objects without DB records older than 24 hours.

---

### Geocoding

#### `property.geocoding.forward`

**Trigger:** Property created/updated with address but no coordinates  
**Queue:** `property.geocoding`

```
1. Call geocoding provider with address
2. Update property location (lat, lng, geohash, PostGIS point)
3. Update property_addresses
4. Emit PropertyLocationChanged event
```

**Retry:** 2x  
**Rate limit:** Respect provider limits (Nominatim: 1 req/sec)

#### `property.geocoding.reverse`

**Trigger:** Property created with coordinates but no address  
**Queue:** `property.geocoding`

```
1. Call reverse geocoding
2. Populate address components
3. Emit PropertyLocationChanged event
```

---

### Import Jobs

#### `property.import.bulk`

**Trigger:** POST /bulk/import (async mode)  
**Queue:** `property.import`

```
1. Create job record in Redis/DB
2. For each item:
   a. Parse source (URL, address, coordinates)
   b. Check duplicates
   c. Create property via factory
   d. Queue geocoding if needed
   e. Update job progress
3. Emit PropertyImported event with summary
4. Mark job completed/failed
```

**Batch size:** Process 10 items per sub-task (chord pattern)  
**Max items:** 10,000 per job  
**Timeout:** 30 minutes

#### `property.import.from_listing_url`

**Trigger:** POST /register with source_type=listing_url  
**Queue:** `property.import`

```
1. Fetch listing page via adapter
2. Extract metadata (title, price, location, images)
3. Map to domain model via anti-corruption layer
4. Create property
5. Queue image downloads
6. Queue geocoding
```

---

### External Sync

#### `property.sync.listing`

**Trigger:** Celery beat (every 6 hours for active listings)  
**Queue:** `property.sync`

```
1. Fetch latest listing data from provider
2. Diff with current property state
3. Update changed fields (price, status, description)
4. Emit PropertyUpdated / PropertyPriceChanged as needed
```

#### `property.sync.listing_single`

**Trigger:** Manual refresh via API  
**Queue:** `property.sync`

---

### Outbox Processing

#### `property.outbox.publish`

**Trigger:** Celery beat (every 5 seconds)  
**Queue:** `property.outbox`

```
1. SELECT pending events FROM outbox_events
   FOR UPDATE SKIP LOCKED LIMIT 100
2. Serialize to CloudEvents
3. Publish to RabbitMQ exchange property.events
4. Mark events as published
5. On failure: increment retry_count, exponential backoff
6. After 5 failures: move to DLQ, alert
```

---

### Maintenance

#### `property.maintenance.refresh_statistics`

**Trigger:** Celery beat (every 30 minutes)  
**Queue:** `property.maintenance`

Pre-compute and cache tenant statistics.

#### `property.maintenance.purge_outbox`

**Trigger:** Celery beat (daily 04:00 UTC)  
**Queue:** `property.maintenance`

Delete published outbox events older than 7 days.

#### `property.maintenance.create_version_snapshot`

**Trigger:** After significant property updates (chained task)  
**Queue:** `property.default`

Create immutable version snapshot in `property_versions`.

#### `property.maintenance.update_search_vector`

**Trigger:** After property text field updates  
**Queue:** `property.default`

Refresh PostgreSQL `tsvector` for full-text search.

---

## Celery Configuration

```python
# infrastructure/celery/app.py

celery_app = Celery("property_service")
celery_app.config_from_object({
    "broker_url": settings.RABBITMQ_URL,
    "result_backend": settings.REDIS_URL,
    "task_serializer": "json",
    "result_serializer": "json",
    "accept_content": ["json"],
    "task_track_started": True,
    "task_acks_late": True,
    "worker_prefetch_multiplier": 1,
    "task_default_queue": "property.default",
    "task_routes": {
        "property.image.*": {"queue": "property.image"},
        "property.import.*": {"queue": "property.import"},
        "property.geocoding.*": {"queue": "property.geocoding"},
        "property.sync.*": {"queue": "property.sync"},
        "property.outbox.*": {"queue": "property.outbox"},
        "property.maintenance.*": {"queue": "property.maintenance"},
    },
    "beat_schedule": {
        "publish-outbox": {
            "task": "property.outbox.publish",
            "schedule": 5.0,
        },
        "refresh-statistics": {
            "task": "property.maintenance.refresh_statistics",
            "schedule": crontab(minute="*/30"),
        },
        "sync-listings": {
            "task": "property.sync.listing",
            "schedule": crontab(hour="*/6"),
        },
        "cleanup-orphaned-images": {
            "task": "property.image.cleanup_orphaned",
            "schedule": crontab(hour=3, minute=0),
        },
        "purge-outbox": {
            "task": "property.maintenance.purge_outbox",
            "schedule": crontab(hour=4, minute=0),
        },
    },
})
```

---

## Job Status Tracking

Bulk jobs tracked in Redis:

```json
{
  "job_id": "uuid",
  "type": "bulk_import",
  "status": "processing",
  "total_items": 150,
  "processed": 87,
  "created": 82,
  "skipped": 3,
  "failed": 2,
  "errors": [
    { "index": 45, "source_reference": "https://...", "error": "DUPLICATE_LISTING" }
  ],
  "started_at": "2026-06-30T12:00:00Z",
  "updated_at": "2026-06-30T12:05:00Z"
}
```

**TTL:** 7 days after completion.

---

## Error Handling in Tasks

| Failure Type | Action |
|-------------|--------|
| Transient (network, timeout) | Retry with backoff |
| Permanent (validation, duplicate) | Log, skip item, continue batch |
| Infrastructure (DB down) | Retry, then DLQ + alert |
| Rate limited (geocoding) | Retry with `countdown=60` |

---

## Monitoring

| Metric | Description |
|--------|-------------|
| `celery_tasks_total` | Counter by task name and status |
| `celery_task_duration_seconds` | Histogram per task |
| `celery_queue_length` | Gauge per queue |
| `celery_dlq_size` | Alert if > 0 |
| `import_job_duration_seconds` | Histogram for bulk imports |
