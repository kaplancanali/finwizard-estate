# 7. Service Responsibilities

## Responsibility Matrix

| Capability | Property Service | Other Services |
|------------|:--------------:|:--------------:|
| Property CRUD | ✅ | |
| Property Search | ✅ | |
| Property Images/Docs storage refs | ✅ | |
| Geocoding orchestration | ✅ (trigger) | Geocoding Provider |
| Image processing | ✅ (trigger) | |
| Listing import/scrape | ✅ (adapter) | |
| Investment analysis | | ✅ Investment Service |
| Price prediction | | ✅ Valuation Service |
| Risk/earthquake analysis | | ✅ Risk Service |
| AI photo/street/satellite | | ✅ Vision AI Services |
| Recommendations | | ✅ Recommendation Service |
| Market analysis | | ✅ Market Intelligence |
| User authentication | | ✅ Identity Service |
| Notifications delivery | | ✅ Notification Service |

---

## Application Services

### PropertyApplicationService

**Responsibility:** Orchestrate property lifecycle commands.

| Method | Description |
|--------|-------------|
| `create_property` | Validate → generate code/slug → persist → emit PropertyCreated |
| `update_property` | Optimistic lock check → diff changes → persist → emit events |
| `delete_property` | Soft delete → emit PropertyDeleted |
| `restore_property` | Undelete → emit PropertyUpdated |
| `change_status` | State machine validation → history → emit PropertyStatusChanged |
| `register_from_source` | Delegate to factory → async if needed |

**Dependencies:** PropertyRepository, UnitOfWork, PropertyCodeGenerator, SlugGenerator, OutboxRepository, PropertyCache

---

### PropertySearchService

**Responsibility:** Read-side search orchestration (CQRS query handler).

| Method | Description |
|--------|-------------|
| `search` | Compose filters → check cache → query repository → cache results |
| `find_nearby` | Radius search with distance sorting |
| `map_search` | Bounding box / cluster aggregation |
| `autocomplete` | Location/type suggestions (Phase 2) |

**Dependencies:** PropertySearchRepository, SearchCache

**Does NOT:** Mutate property state.

---

### PropertyMediaService

**Responsibility:** Media upload lifecycle.

| Method | Description |
|--------|-------------|
| `initiate_image_upload` | Create record → generate presigned URL |
| `confirm_image_upload` | Verify object exists → queue thumbnail task |
| `reorder_images` | Update sort order → emit PropertyImagesUpdated |
| `delete_image` | Soft delete → invalidate cache → emit event |
| `initiate_document_upload` | Same pattern for documents |
| `verify_document` | Admin verification |

**Dependencies:** PropertyRepository, ObjectStorage, Celery tasks, PropertyCache

---

### PropertyImportService

**Responsibility:** Bulk and external source import.

| Method | Description |
|--------|-------------|
| `import_from_listing_url` | Adapter → map to domain → deduplicate → create |
| `bulk_import` | Queue Celery job → process batch → emit PropertyImported |
| `sync_listing` | Re-fetch external listing → update changed fields |

**Dependencies:** ListingAdapters, PropertyFactory, Celery, PropertyMergeService

---

### PropertyHistoryService

**Responsibility:** Read-only history and versioning.

| Method | Description |
|--------|-------------|
| `get_price_history` | Paginated price changes |
| `get_status_history` | Status transitions |
| `get_ownership_history` | Ownership timeline |
| `get_versions` | Version snapshots |
| `get_audit_logs` | Full audit trail (admin) |

**Dependencies:** PropertyRepository, PropertyVersionRepository

---

### PropertyStatisticsService

**Responsibility:** Aggregated analytics (property data only, no market analysis).

| Method | Description |
|--------|-------------|
| `get_tenant_statistics` | Counts by type, status, location |
| `get_price_distribution` | Min/max/avg/median within tenant scope |

**Dependencies:** PropertySearchRepository, Redis (cached aggregates)

---

## Domain Services

### PropertyCodeGenerator

- Format: `FW-{COUNTRY}-{REGION_CODE}-{SEQUENCE:08d}`
- Sequence per tenant per region (PostgreSQL sequence or atomic counter)
- Thread-safe, no collisions

### SlugGenerator

- Slugify title + district
- Check uniqueness per tenant
- Append numeric suffix on collision (`-2`, `-3`)

### PropertyValidator

- Cross-field rules: construction_year ≤ current year
- net_area ≤ gross_area
- room_count > 0 for residential types
- coordinates required if no address
- price required if status = listed

### PropertyMergeService

- Detect duplicates by: same listing_id, same parcel, proximity + similar attributes
- Merge strategy: keep newer, merge metadata, link as aliases (Phase 2)

### GeocodingService (interface)

- `geocode(address) → coordinates`
- `reverse_geocode(lat, lng) → address components`
- Implementation in infrastructure (Nominatim, Google, Mapbox)

---

## Infrastructure Services

### OutboxProcessor

- Poll `outbox_events` WHERE status = 'pending'
- Serialize to CloudEvents → publish to RabbitMQ
- Mark published / handle failures

### PropertyCacheManager

- Cache-aside for property details, search results, statistics
- Event-driven invalidation on domain events

### ObjectStorageService

- S3/MinIO presigned URL generation
- Key pattern: `{tenant_id}/properties/{property_id}/images/{image_id}.{ext}`

---

## API Layer Responsibilities

| Concern | Owner |
|---------|-------|
| Request validation | Pydantic schemas |
| Authentication | JWT middleware |
| Authorization | RBAC dependency |
| Rate limiting | Redis-based middleware |
| Idempotency | Redis idempotency store |
| Correlation ID | Middleware injection |
| Error mapping | Exception handlers |
| OpenAPI generation | FastAPI auto-docs |

---

## What This Service Owns (SSOT)

1. Property identity (UUID, code, slug)
2. All property attributes and classifications
3. Location and parcel data
4. Media and document references (not binary storage)
5. Ownership records
6. Price/status/ownership history
7. Version snapshots
8. Audit logs
9. Search index (Phase 1: PostgreSQL; Phase 3: ES projection)
10. Property metadata and tenant extensions

## What This Service Does NOT Own

1. User/tenant management (Identity Service)
2. Binary file storage (Object Storage / CDN)
3. Email/push notifications (Notification Service)
4. Any analytical computation on property data
5. External listing data (cached via adapters, SSOT remains here after import)
