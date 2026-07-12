# 5. API Contract

## Base URL & Versioning

| Item | Value |
|------|-------|
| Base path | `/api/v1` |
| Content-Type | `application/json` |
| Auth | `Authorization: Bearer <JWT>` |
| Idempotency | `Idempotency-Key: <uuid>` on POST/PUT/PATCH |
| Correlation | `X-Correlation-ID: <uuid>` (optional, generated if absent) |
| Tenant | `X-Tenant-ID: <uuid>` (enterprise override, validated against JWT) |

## Common Response Envelope

### Success (single resource)

```json
{
  "data": { },
  "meta": {
    "correlation_id": "uuid",
    "request_id": "uuid"
  }
}
```

### Success (collection)

```json
{
  "data": [ ],
  "pagination": {
    "page": 1,
    "page_size": 20,
    "total_items": 1542,
    "total_pages": 78,
    "has_next": true,
    "has_previous": false
  },
  "meta": {
    "correlation_id": "uuid"
  }
}
```

### Error

```json
{
  "error": {
    "code": "PROPERTY_NOT_FOUND",
    "message": "Property with id '...' was not found",
    "details": [],
    "correlation_id": "uuid"
  }
}
```

---

## Properties — CRUD

### `POST /api/v1/properties`

Create a property (manual entry or from source).

**Permissions:** `property:create`

**Request:**

```json
{
  "title": "Modern Apartment in Kadıköy",
  "description": "Spacious 3+1 apartment with sea view",
  "property_type": "apartment",
  "property_category": "residential",
  "status": "draft",
  "visibility": "private",
  "pricing": {
    "sale_price": 8500000.00,
    "currency": "TRY",
    "maintenance_fee": 2500.00
  },
  "location": {
    "country_code": "TR",
    "province": "İstanbul",
    "district": "Kadıköy",
    "neighborhood": "Moda",
    "street": "Bahariye Cd.",
    "postal_code": "34710",
    "latitude": 40.9876,
    "longitude": 29.0234
  },
  "building": {
    "construction_year": 2018,
    "floor_number": 5,
    "unit_number": "12",
    "net_area_sqm": 145.5,
    "gross_area_sqm": 165.0,
    "room_count": 3.5,
    "bathroom_count": 2,
    "balcony_count": 1,
    "parking_count": 1
  },
  "features": {
    "heating_type": "central",
    "has_elevator": true,
    "has_parking": true,
    "has_balcony": true,
    "energy_certificate_class": "B"
  },
  "amenities": ["security", "gym", "concierge"],
  "tags": ["sea-view", "renovated"],
  "source": {
    "source_type": "manual"
  }
}
```

**Response:** `201 Created` — full property object with `property_code`, `slug`, `id`, `version`.

---

### `GET /api/v1/properties/{property_id}`

**Permissions:** `property:read`

**Query params:** `include=images,documents,ownership,history,listing` (comma-separated)

**Response:** `200 OK`

---

### `GET /api/v1/properties/code/{property_code}`

Lookup by human-readable code.

**Response:** `200 OK` | `404`

---

### `GET /api/v1/properties/slug/{slug}`

Lookup by slug (tenant-scoped).

---

### `PUT /api/v1/properties/{property_id}`

Full replacement update. Requires `version` for optimistic locking.

**Permissions:** `property:update`

**Headers:** `If-Match: <version>` or `version` in body.

**Response:** `200 OK` | `409 Conflict` (version mismatch)

---

### `PATCH /api/v1/properties/{property_id}`

Partial update (JSON Merge Patch semantics).

**Request:**

```json
{
  "version": 3,
  "title": "Updated Title",
  "pricing": { "sale_price": 8200000.00 }
}
```

---

### `DELETE /api/v1/properties/{property_id}`

Soft delete.

**Permissions:** `property:delete`

**Response:** `204 No Content`

---

### `POST /api/v1/properties/{property_id}/restore`

Restore soft-deleted property.

**Permissions:** `property:delete` (admin)

**Response:** `200 OK`

---

## Bulk Operations

### `POST /api/v1/properties/bulk/import`

**Permissions:** `property:bulk_import`

**Request:**

```json
{
  "source_type": "listing_url",
  "items": [
    { "source_reference": "https://..." },
    { "source_reference": "https://..." }
  ],
  "options": {
    "async": true,
    "skip_duplicates": true,
    "default_status": "draft"
  }
}
```

**Response (async):** `202 Accepted`

```json
{
  "data": {
    "job_id": "uuid",
    "status": "queued",
    "total_items": 150
  }
}
```

---

### `PATCH /api/v1/properties/bulk/update`

**Permissions:** `property:bulk_update`

**Request:**

```json
{
  "filter": { "status": "draft", "property_type": "apartment" },
  "updates": { "status": "active" },
  "options": { "async": true, "max_items": 1000 }
}
```

---

### `DELETE /api/v1/properties/bulk`

**Permissions:** `property:bulk_delete`

**Request:**

```json
{
  "property_ids": ["uuid1", "uuid2"],
  "options": { "hard_delete": false }
}
```

---

### `GET /api/v1/properties/bulk/jobs/{job_id}`

Poll bulk job status.

---

## Search

### `POST /api/v1/properties/search`

Primary search endpoint (complex filters in body).

**Permissions:** `property:search`

**Request:**

```json
{
  "query": "kadıköy deniz manzaralı",
  "filters": {
    "property_types": ["apartment", "residence"],
    "property_categories": ["residential"],
    "status": ["active", "listed"],
    "sale_price": { "min": 5000000, "max": 15000000 },
    "rental_price": { "min": null, "max": null },
    "net_area_sqm": { "min": 100, "max": 200 },
    "room_count": { "min": 2, "max": 4 },
    "bathroom_count": { "min": 1 },
    "construction_year": { "min": 2010 },
    "country_code": "TR",
    "provinces": ["İstanbul"],
    "districts": ["Kadıköy", "Beşiktaş"],
    "heating_types": ["central", "floor"],
    "amenities": ["pool", "security"],
    "features": {
      "has_elevator": true,
      "has_parking": true,
      "has_pool": false
    },
    "tags": ["sea-view"]
  },
  "geo": {
    "type": "radius",
    "latitude": 40.9876,
    "longitude": 29.0234,
    "radius_meters": 5000
  },
  "sort": [
    { "field": "sale_price", "direction": "asc" },
    { "field": "created_at", "direction": "desc" }
  ],
  "pagination": { "page": 1, "page_size": 20 },
  "include_facets": true
}
```

**Geo filter types:**

| Type | Fields |
|------|--------|
| `radius` | `latitude`, `longitude`, `radius_meters` |
| `bounding_box` | `north`, `south`, `east`, `west` |
| `polygon` | `coordinates: [[lng, lat], ...]` (GeoJSON) |

**Response:** `200 OK` with paginated property summaries + optional facets.

---

### `GET /api/v1/properties/search`

Simple search via query params (lightweight clients).

**Query params:** `q`, `type`, `status`, `min_price`, `max_price`, `min_area`, `max_area`, `rooms`, `province`, `district`, `lat`, `lng`, `radius`, `sort`, `page`, `page_size`

---

### `GET /api/v1/properties/nearby`

**Query params:** `lat`, `lng`, `radius` (meters, default 5000), `limit` (default 20), `property_type`, `status`

**Response:** Properties sorted by distance with `distance_meters` field.

---

### `GET /api/v1/properties/map`

Map cluster endpoint for bounding box.

**Query params:** `north`, `south`, `east`, `west`, `zoom`, `cluster`

**Response:** Clustered points or individual markers based on zoom level.

---

## History & Versions

### `GET /api/v1/properties/{property_id}/history/price`

Paginated price history.

### `GET /api/v1/properties/{property_id}/history/status`

Status transition history.

### `GET /api/v1/properties/{property_id}/history/ownership`

Ownership history.

### `GET /api/v1/properties/{property_id}/versions`

List version snapshots.

### `GET /api/v1/properties/{property_id}/versions/{version_number}`

Retrieve specific version snapshot.

### `GET /api/v1/properties/{property_id}/audit-logs`

Audit log (admin only). **Permissions:** `property:audit`

---

## Images

### `POST /api/v1/properties/{property_id}/images`

Upload image metadata + presigned upload URL.

**Request:**

```json
{
  "file_name": "living-room.jpg",
  "mime_type": "image/jpeg",
  "file_size": 2048000,
  "caption": "Living room",
  "is_primary": true,
  "sort_order": 0
}
```

**Response:** `201` with `upload_url` (presigned S3) and `image` record.

### `POST /api/v1/properties/{property_id}/images/{image_id}/confirm`

Confirm upload completed; triggers thumbnail processing.

### `PATCH /api/v1/properties/{property_id}/images/reorder`

**Request:** `{ "image_ids": ["uuid1", "uuid2", ...] }`

### `DELETE /api/v1/properties/{property_id}/images/{image_id}`

---

## Documents

### `POST /api/v1/properties/{property_id}/documents`

Same presigned upload pattern as images.

### `DELETE /api/v1/properties/{property_id}/documents/{document_id}`

### `PATCH /api/v1/properties/{property_id}/documents/{document_id}/verify`

Admin verification. **Permissions:** `property:verify_documents`

---

## Metadata

### `GET /api/v1/properties/{property_id}/metadata`

### `PATCH /api/v1/properties/{property_id}/metadata`

**Request:**

```json
{
  "metadata": { "custom_field": "value" },
  "tenant_extensions": { "crm_id": "EXT-12345" }
}
```

---

## Status Management

### `POST /api/v1/properties/{property_id}/status`

**Request:**

```json
{
  "version": 3,
  "status": "active",
  "reason": "Approved by admin"
}
```

---

## Registration from Source

### `POST /api/v1/properties/register`

Create property from external source (async for URL/OCR).

**Request:**

```json
{
  "source_type": "listing_url",
  "source_reference": "https://www.sahibinden.com/...",
  "options": {
    "auto_geocode": true,
    "default_status": "draft"
  }
}
```

**Source types:** `manual`, `listing_url`, `address`, `coordinates`, `map_selection`, `parcel`

---

## Statistics

### `GET /api/v1/properties/statistics`

**Query params:** `tenant_id` (admin), `group_by` (type, status, province, district)

**Response:**

```json
{
  "data": {
    "total_count": 125000,
    "by_status": { "active": 98000, "draft": 12000 },
    "by_type": { "apartment": 75000, "villa": 15000 },
    "by_province": { "İstanbul": 45000, "Ankara": 22000 },
    "price_stats": {
      "avg_sale_price": 6500000,
      "median_sale_price": 5200000,
      "currency": "TRY"
    }
  }
}
```

---

## Lookup Endpoints

### `GET /api/v1/lookups/property-types`

### `GET /api/v1/lookups/amenities`

### `GET /api/v1/lookups/statuses`

---

## Health & Observability

### `GET /health` — Liveness

### `GET /health/ready` — Readiness (DB, Redis, RabbitMQ)

### `GET /metrics` — Prometheus metrics (internal)

---

## HTTP Status Code Mapping

| Code | Usage |
|------|-------|
| 200 | Success |
| 201 | Created |
| 202 | Accepted (async job) |
| 204 | Deleted |
| 400 | Validation error |
| 401 | Unauthenticated |
| 403 | Forbidden |
| 404 | Not found |
| 409 | Concurrency conflict / duplicate |
| 422 | Unprocessable (business rule) |
| 429 | Rate limited |
| 500 | Internal error |
| 503 | Service unavailable |

---

## Rate Limits

| Tier | Requests/min | Bulk ops/hour |
|------|-------------|---------------|
| Mobile | 120 | 10 |
| Web | 200 | 20 |
| Enterprise API | 1000 | 100 |
| Partner API | 500 | 50 |

Headers: `X-RateLimit-Limit`, `X-RateLimit-Remaining`, `X-RateLimit-Reset`

---

## OpenAPI

Auto-generated from FastAPI at `/api/v1/openapi.json` and `/api/v1/docs` (disabled in production).

Export script: `scripts/generate_openapi.py` → committed `openapi/v1/property-service.yaml` for consumer SDK generation.
