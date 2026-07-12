# 10. Validation Rules

Validation occurs at three levels: **input validation** (Pydantic), **domain validation** (aggregate invariants), and **business rules** (application service).

---

## Input Validation (Pydantic — Presentation Layer)

### Field Constraints

| Field | Rule |
|-------|------|
| `title` | Required, 3–500 chars, no-only-whitespace |
| `description` | Max 10,000 chars |
| `property_type` | Must be valid enum or active lookup value |
| `property_category` | Must be valid enum |
| `country_code` | ISO 3166-1 alpha-2 |
| `currency` | ISO 4217 (3 chars) |
| `latitude` | -90 to 90, max 6 decimal places |
| `longitude` | -180 to 180, max 6 decimal places |
| `sale_price` | ≥ 0, max 15 digits + 2 decimal |
| `rental_price` | ≥ 0 |
| `net_area_sqm` | > 0, max 999,999.99 |
| `gross_area_sqm` | > 0 |
| `room_count` | > 0, supports 0.5 increments |
| `construction_year` | 1800–(current_year + 5) |
| `tags` | Max 20 tags, each max 100 chars |
| `amenities` | Each must exist in `amenity_definitions` |
| `file_size` (image) | Max 20 MB |
| `file_size` (document) | Max 50 MB |
| `mime_type` (image) | image/jpeg, image/png, image/webp, image/gif |
| `bulk import items` | Max 500 per request |
| `search page_size` | 1–100 |
| `geo radius` | Max 100,000 meters |

---

## Domain Validation (Aggregate Invariants)

### Property Creation

| Rule ID | Rule | Error Code |
|---------|------|------------|
| DV-001 | Must have address components OR valid coordinates | `LOCATION_REQUIRED` |
| DV-002 | `property_type` must belong to `property_category` | `TYPE_CATEGORY_MISMATCH` |
| DV-003 | Land type must not have building fields (floor, rooms) | `INVALID_FIELDS_FOR_TYPE` |
| DV-004 | Commercial/industrial types may omit room_count | `—` (allowed) |
| DV-005 | Currency required when any price is set | `CURRENCY_REQUIRED` |
| DV-006 | Only one primary image allowed | `MULTIPLE_PRIMARY_IMAGES` |

### Property Update

| Rule ID | Rule | Error Code |
|---------|------|------------|
| DV-010 | `property_code` is immutable | `IMMUTABLE_FIELD` |
| DV-011 | `version` must match current (optimistic lock) | `CONCURRENCY_CONFLICT` |
| DV-012 | Cannot update soft-deleted property | `PROPERTY_DELETED` |
| DV-013 | `net_area_sqm` ≤ `gross_area_sqm` when both set | `AREA_INVALID` |
| DV-014 | `floor_number` ≤ `floor_count` when both set | `FLOOR_INVALID` |
| DV-015 | `construction_year` ≤ current year (unless under_construction flag) | `INVALID_CONSTRUCTION_YEAR` |

### Status Transitions

| Rule ID | Rule | Error Code |
|---------|------|------------|
| DV-020 | Transitions must follow state machine | `INVALID_STATUS_TRANSITION` |
| DV-021 | `listed` requires sale_price OR rental_price OR price_on_request | `PRICE_REQUIRED_FOR_LISTING` |
| DV-022 | `listed` requires at least one image | `IMAGE_REQUIRED_FOR_LISTING` |
| DV-023 | `active` requires location with coordinates | `COORDINATES_REQUIRED` |
| DV-024 | `deleted` is terminal (only restore allowed) | `INVALID_STATUS_TRANSITION` |

### Valid Transitions Matrix

| From \ To | draft | pending | active | listed | inactive | archived | deleted |
|-----------|:-----:|:-------:|:------:|:------:|:--------:|:--------:|:-------:|
| draft | — | ✅ | ✅ | ❌ | ❌ | ✅ | ✅ |
| pending | ✅ | — | ✅ | ❌ | ❌ | ✅ | ✅ |
| active | ❌ | ❌ | — | ✅ | ✅ | ✅ | ✅ |
| listed | ❌ | ❌ | ✅ | — | ✅ | ✅ | ✅ |
| inactive | ✅ | ❌ | ✅ | ✅ | — | ✅ | ✅ |
| archived | ❌ | ❌ | ❌ | ❌ | ❌ | — | ✅ |
| deleted | ✅(restore) | ❌ | ❌ | ❌ | ❌ | ❌ | — |

### Ownership

| Rule ID | Rule | Error Code |
|---------|------|------------|
| DV-030 | Total ownership_percentage ≤ 100 | `OWNERSHIP_EXCEEDS_100` |
| DV-031 | Only one `is_current=true` per owner_type+name combo | `DUPLICATE_OWNER` |
| DV-032 | `released_at` must be ≥ `acquired_at` | `INVALID_OWNERSHIP_DATES` |

### Listing Import

| Rule ID | Rule | Error Code |
|---------|------|------------|
| DV-040 | Duplicate `provider + listing_id` rejected (unless skip_duplicates) | `DUPLICATE_LISTING` |
| DV-041 | Invalid listing URL format | `INVALID_LISTING_URL` |
| DV-042 | Unsupported listing provider | `UNSUPPORTED_PROVIDER` |

---

## Business Validation (Application Layer)

| Rule ID | Rule | Error Code |
|---------|------|------------|
| BV-001 | User must have `property:create` permission | `FORBIDDEN` |
| BV-002 | Tenant scope: property belongs to user's tenant | `TENANT_MISMATCH` |
| BV-003 | Bulk update max 1,000 items per job | `BULK_LIMIT_EXCEEDED` |
| BV-004 | Rate limit not exceeded | `RATE_LIMIT_EXCEEDED` |
| BV-005 | Idempotency key not reused with different payload | `IDEMPOTENCY_CONFLICT` |
| BV-006 | Partner API: only `visibility=public` or `partner` properties readable | `FORBIDDEN` |

---

## Cross-Field Validation Examples

```python
# PropertyValidator (domain service)

def validate_pricing(property_type, pricing, status):
  if status == LISTED and not pricing.price_on_request:
    if not pricing.sale_price and not pricing.rental_price:
      raise ValidationError("PRICE_REQUIRED_FOR_LISTING")

def validate_building_for_type(property_type, building):
  if property_type == LAND and building:
    if building.floor_number or building.room_count:
      raise ValidationError("INVALID_FIELDS_FOR_TYPE")

def validate_area(building):
  if building.net_area_sqm and building.gross_area_sqm:
    if building.net_area_sqm > building.gross_area_sqm:
      raise ValidationError("AREA_INVALID")
```

---

## Metadata JSON Schema Validation

`property_metadata.metadata` validated against JSON Schema per `property_type`:

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "type": "object",
  "properties": {
    "custom_field": { "type": "string", "maxLength": 500 },
    "energy_consumption_kwh": { "type": "number", "minimum": 0 }
  },
  "additionalProperties": false
}
```

Schemas stored in `config/metadata_schemas/{property_type}.json`.

---

## Validation Error Response Format

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Request validation failed",
    "details": [
      {
        "field": "building.net_area_sqm",
        "message": "Net area cannot exceed gross area",
        "code": "AREA_INVALID"
      },
      {
        "field": "status",
        "message": "Cannot transition from 'draft' to 'listed'",
        "code": "INVALID_STATUS_TRANSITION"
      }
    ],
    "correlation_id": "uuid"
  }
}
```

HTTP status: **422 Unprocessable Entity** for domain/business rules, **400 Bad Request** for Pydantic input validation.
