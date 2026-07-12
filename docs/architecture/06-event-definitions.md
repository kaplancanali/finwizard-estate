# 6. Event Definitions

## Event Architecture

```
Property Aggregate
       │
       ▼
  Domain Event (in-memory)
       │
       ▼
  Outbox Table (same transaction)
       │
       ▼
  Outbox Processor (Celery beat)
       │
       ▼
  RabbitMQ Exchange: property.events
       │
       ├──► Valuation Service
       ├──► Risk Service
       ├──► Search Indexer (future ES)
       ├──► Notification Service
       └──► Analytics Pipeline (future Kafka)
```

### Design Principles

1. **Transactional Outbox** — events persisted in same DB transaction as aggregate change
2. **At-least-once delivery** — consumers must be idempotent
3. **CloudEvents 1.0** envelope for interoperability
4. **Schema versioning** — `event_version` field on every event
5. **Future Kafka** — RabbitMQ topology maps 1:1 to Kafka topics

---

## Exchange & Routing

| RabbitMQ Exchange | Type | Purpose |
|-------------------|------|---------|
| `property.events` | topic | All property domain events |
| `property.events.dlx` | fanout | Dead letter exchange |

### Routing Keys

Pattern: `property.<event_name_lowercase>.v<version>`

Examples:
- `property.created.v1`
- `property.price_changed.v1`
- `property.location_changed.v1`

### Queues (per consumer)

| Queue | Binding | Consumer |
|-------|---------|----------|
| `valuation.property.events` | `property.price_changed.v1` | Valuation Service |
| `risk.property.events` | `property.location_changed.v1` | Risk Service |
| `search.property.events` | `property.*.v1` | Search Indexer |
| `notification.property.events` | `property.status_changed.v1`, `property.created.v1` | Notification Service |

---

## CloudEvents Envelope

```json
{
  "specversion": "1.0",
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "source": "property-service",
  "type": "com.finward.property.created.v1",
  "datacontenttype": "application/json",
  "time": "2026-06-30T12:00:00Z",
  "subject": "property/{property_id}",
  "correlationid": "uuid",
  "tenantid": "uuid",
  "data": { }
}
```

---

## Event Catalog

### PropertyCreated

**Type:** `com.finward.property.created.v1`  
**Trigger:** New property registered  
**Routing Key:** `property.created.v1`

```json
{
  "property_id": "uuid",
  "tenant_id": "uuid",
  "property_code": "FW-TR-IST-00001234",
  "slug": "modern-apartment-kadikoy",
  "property_type": "apartment",
  "property_category": "residential",
  "status": "draft",
  "source_type": "manual",
  "location": {
    "country_code": "TR",
    "province": "İstanbul",
    "district": "Kadıköy",
    "latitude": 40.9876,
    "longitude": 29.0234
  },
  "pricing": {
    "sale_price": 8500000.00,
    "currency": "TRY"
  },
  "created_by": "uuid",
  "created_at": "2026-06-30T12:00:00Z"
}
```

---

### PropertyUpdated

**Type:** `com.finward.property.updated.v1`  
**Trigger:** Any field change on property  
**Routing Key:** `property.updated.v1`

```json
{
  "property_id": "uuid",
  "tenant_id": "uuid",
  "property_code": "FW-TR-IST-00001234",
  "version": 4,
  "changed_fields": ["title", "description", "pricing.sale_price"],
  "changes": {
    "title": { "old": "Old Title", "new": "New Title" },
    "pricing.sale_price": { "old": 8500000.00, "new": 8200000.00 }
  },
  "updated_by": "uuid",
  "updated_at": "2026-06-30T12:05:00Z"
}
```

---

### PropertyDeleted

**Type:** `com.finward.property.deleted.v1`  
**Trigger:** Soft delete  
**Routing Key:** `property.deleted.v1`

```json
{
  "property_id": "uuid",
  "tenant_id": "uuid",
  "property_code": "FW-TR-IST-00001234",
  "deleted_by": "uuid",
  "deleted_at": "2026-06-30T12:10:00Z",
  "hard_delete": false
}
```

---

### PropertyImported

**Type:** `com.finward.property.imported.v1`  
**Trigger:** Bulk import job completed (per property or batch summary)  
**Routing Key:** `property.imported.v1`

```json
{
  "job_id": "uuid",
  "tenant_id": "uuid",
  "source_type": "listing_url",
  "summary": {
    "total": 150,
    "created": 142,
    "skipped": 5,
    "failed": 3
  },
  "created_property_ids": ["uuid1", "uuid2"],
  "failed_items": [
    { "source_reference": "https://...", "error": "DUPLICATE_LISTING" }
  ],
  "completed_at": "2026-06-30T12:15:00Z"
}
```

---

### PropertyPriceChanged

**Type:** `com.finward.property.price_changed.v1`  
**Trigger:** Sale, rental, or maintenance fee change  
**Routing Key:** `property.price_changed.v1`

```json
{
  "property_id": "uuid",
  "tenant_id": "uuid",
  "property_code": "FW-TR-IST-00001234",
  "price_type": "sale",
  "old_amount": 8500000.00,
  "new_amount": 8200000.00,
  "currency": "TRY",
  "price_per_sqm": 56357.39,
  "changed_by": "uuid",
  "changed_at": "2026-06-30T12:05:00Z",
  "change_reason": "Market adjustment"
}
```

---

### PropertyLocationChanged

**Type:** `com.finward.property.location_changed.v1`  
**Trigger:** Address or coordinates change  
**Routing Key:** `property.location_changed.v1`

```json
{
  "property_id": "uuid",
  "tenant_id": "uuid",
  "property_code": "FW-TR-IST-00001234",
  "old_location": {
    "latitude": 40.9876,
    "longitude": 29.0234,
    "province": "İstanbul",
    "district": "Kadıköy"
  },
  "new_location": {
    "latitude": 41.0082,
    "longitude": 28.9784,
    "province": "İstanbul",
    "district": "Fatih"
  },
  "geocoded": true,
  "changed_by": "uuid",
  "changed_at": "2026-06-30T12:20:00Z"
}
```

---

### PropertyStatusChanged

**Type:** `com.finward.property.status_changed.v1`  
**Trigger:** Status state machine transition  
**Routing Key:** `property.status_changed.v1`

```json
{
  "property_id": "uuid",
  "tenant_id": "uuid",
  "property_code": "FW-TR-IST-00001234",
  "old_status": "draft",
  "new_status": "active",
  "reason": "Approved by admin",
  "changed_by": "uuid",
  "changed_at": "2026-06-30T12:25:00Z"
}
```

---

### PropertyImagesUpdated

**Type:** `com.finward.property.images_updated.v1`  
**Trigger:** Image add, remove, reorder, or primary change  
**Routing Key:** `property.images_updated.v1`

```json
{
  "property_id": "uuid",
  "tenant_id": "uuid",
  "action": "added",
  "image_ids": ["uuid"],
  "primary_image_id": "uuid",
  "total_images": 12,
  "updated_by": "uuid",
  "updated_at": "2026-06-30T12:30:00Z"
}
```

---

### PropertyDocumentsUpdated

**Type:** `com.finward.property.documents_updated.v1`  
**Trigger:** Document add, remove, or verify  
**Routing Key:** `property.documents_updated.v1`

```json
{
  "property_id": "uuid",
  "tenant_id": "uuid",
  "action": "added",
  "document_ids": ["uuid"],
  "document_types": ["property_deed"],
  "updated_by": "uuid",
  "updated_at": "2026-06-30T12:35:00Z"
}
```

---

### PropertyOwnershipChanged

**Type:** `com.finward.property.ownership_changed.v1`  
**Trigger:** Ownership record add/update/release  
**Routing Key:** `property.ownership_changed.v1`

```json
{
  "property_id": "uuid",
  "tenant_id": "uuid",
  "action": "transferred",
  "current_owners": [
    { "owner_name": "John Doe", "ownership_percentage": 100.0 }
  ],
  "changed_by": "uuid",
  "changed_at": "2026-06-30T12:40:00Z"
}
```

---

## Outbox Schema

| Column | Purpose |
|--------|---------|
| `id` | Event UUID |
| `aggregate_id` | Property ID |
| `event_type` | CloudEvents type |
| `payload` | Full event data JSONB |
| `metadata` | correlation_id, tenant_id, actor_id |
| `status` | pending → published → failed |
| `retry_count` | Max 5 retries with exponential backoff |

### Outbox Processor

- Celery beat task every 5 seconds
- Batch size: 100 events
- Publish to RabbitMQ → mark `published_at`
- Failed after 5 retries → move to DLQ + alert

---

## Future Kafka Migration

| RabbitMQ | Kafka Equivalent |
|----------|-----------------|
| Exchange `property.events` | Topic `finward.property.events` |
| Routing key `property.created.v1` | Message key = `property_id`, headers include event type |
| Queue per consumer | Consumer group per service |
| DLX | Dead letter topic `finward.property.events.dlt` |

Dual-write period: outbox processor publishes to both RabbitMQ and Kafka during migration.

---

## Consumer Contract

1. **Idempotency** — deduplicate by CloudEvents `id`
2. **Ordering** — not guaranteed; use `version` for conflict resolution
3. **Retry** — consumer-side retry with backoff; failed messages to DLQ
4. **Schema evolution** — consumers accept `v1` and `v2`; breaking changes require new routing key version
