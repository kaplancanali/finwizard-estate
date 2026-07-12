# 3. Database Design

## Database Engine

- **PostgreSQL 16** with **PostGIS 3.4** extension
- **Schema:** `property` (dedicated schema for service isolation)
- **Encoding:** UTF-8
- **Timezone:** UTC (TIMESTAMPTZ everywhere)

---

## Core Tables

### `properties`

Central aggregate root table. Denormalized search-critical fields for Phase 1 queries.

| Column | Type | Constraints | Notes |
|--------|------|-------------|-------|
| `id` | UUID | PK, DEFAULT gen_random_uuid() | |
| `tenant_id` | UUID | NOT NULL, INDEX | Multi-tenancy |
| `property_code` | VARCHAR(32) | UNIQUE NOT NULL | Immutable |
| `slug` | VARCHAR(255) | NOT NULL | Unique per tenant |
| `title` | VARCHAR(500) | NOT NULL | |
| `description` | TEXT | | |
| `summary` | VARCHAR(1000) | | |
| `property_type` | VARCHAR(50) | NOT NULL, FK | |
| `property_category` | VARCHAR(50) | NOT NULL | |
| `property_subtype` | VARCHAR(100) | | |
| `status` | VARCHAR(30) | NOT NULL, INDEX | |
| `visibility` | VARCHAR(20) | NOT NULL DEFAULT 'private' | |
| `sale_price` | NUMERIC(18,2) | | |
| `rental_price` | NUMERIC(18,2) | | |
| `maintenance_fee` | NUMERIC(18,2) | | |
| `currency` | CHAR(3) | | ISO 4217 |
| `price_on_request` | BOOLEAN | DEFAULT FALSE | |
| `price_per_sqm` | NUMERIC(18,2) | | Computed/denormalized |
| `country_code` | CHAR(2) | NOT NULL | Denormalized from address |
| `province` | VARCHAR(100) | INDEX | |
| `district` | VARCHAR(100) | INDEX | |
| `neighborhood` | VARCHAR(200) | INDEX | |
| `latitude` | NUMERIC(9,6) | | |
| `longitude` | NUMERIC(9,6) | | |
| `location` | GEOGRAPHY(POINT, 4326) | GIST INDEX | PostGIS |
| `geohash` | VARCHAR(12) | INDEX | |
| `net_area_sqm` | NUMERIC(12,2) | INDEX | Denormalized |
| `gross_area_sqm` | NUMERIC(12,2) | | |
| `room_count` | NUMERIC(4,1) | INDEX | |
| `bathroom_count` | SMALLINT | INDEX | |
| `construction_year` | SMALLINT | INDEX | |
| `floor_number` | SMALLINT | | |
| `parking_count` | SMALLINT | | |
| `has_elevator` | BOOLEAN | | Denormalized feature flag |
| `heating_type` | VARCHAR(50) | | |
| `search_vector` | TSVECTOR | GIN INDEX | Full-text search |
| `version` | INTEGER | NOT NULL DEFAULT 1 | Optimistic locking |
| `published_at` | TIMESTAMPTZ | | |
| `created_at` | TIMESTAMPTZ | NOT NULL DEFAULT now() | |
| `updated_at` | TIMESTAMPTZ | NOT NULL DEFAULT now() | |
| `deleted_at` | TIMESTAMPTZ | INDEX | Soft delete |
| `created_by` | UUID | NOT NULL | |
| `updated_by` | UUID | | |

**Constraints:**
- `UNIQUE (tenant_id, slug) WHERE deleted_at IS NULL`
- `UNIQUE (tenant_id, property_code)`
- `CHECK (latitude BETWEEN -90 AND 90)`
- `CHECK (longitude BETWEEN -180 AND 180)`
- `CHECK (version > 0)`

**Indexes:**
```sql
CREATE INDEX idx_properties_tenant_status ON property.properties (tenant_id, status) WHERE deleted_at IS NULL;
CREATE INDEX idx_properties_location ON property.properties USING GIST (location);
CREATE INDEX idx_properties_search_vector ON property.properties USING GIN (search_vector);
CREATE INDEX idx_properties_price ON property.properties (sale_price) WHERE deleted_at IS NULL AND status IN ('active','listed');
CREATE INDEX idx_properties_area ON property.properties (net_area_sqm) WHERE deleted_at IS NULL;
CREATE INDEX idx_properties_type_location ON property.properties (property_type, country_code, province, district);
CREATE INDEX idx_properties_created_at ON property.properties (created_at DESC);
```

---

### `property_addresses`

Normalized address (1:1 with property, allows address history via versioning).

| Column | Type | Constraints |
|--------|------|-------------|
| `id` | UUID | PK |
| `property_id` | UUID | FK → properties, UNIQUE |
| `country_code` | CHAR(2) | NOT NULL |
| `province` | VARCHAR(100) | |
| `district` | VARCHAR(100) | |
| `neighborhood` | VARCHAR(200) | |
| `street` | VARCHAR(300) | |
| `postal_code` | VARCHAR(20) | |
| `address_line` | TEXT | |
| `address_line_2` | TEXT | |
| `latitude` | NUMERIC(9,6) | |
| `longitude` | NUMERIC(9,6) | |
| `elevation` | NUMERIC(8,2) | |
| `location` | GEOGRAPHY(POINT, 4326) | GIST |
| `geohash` | VARCHAR(12) | |
| `timezone` | VARCHAR(50) | |
| `is_verified` | BOOLEAN | DEFAULT FALSE |
| `verified_at` | TIMESTAMPTZ ingest | |
| `created_at` | TIMESTAMPTZ | |
| `updated_at` | TIMESTAMPTZ | |

---

### `property_parcels`

| Column | Type | Constraints |
|--------|------|-------------|
| `id` | UUID | PK |
| `property_id` | UUID | FK → properties, UNIQUE |
| `block` | VARCHAR(50) | |
| `parcel_number` | VARCHAR(50) | |
| `parcel_area_sqm` | NUMERIC(12,2) | |
| `cadastral_reference` | VARCHAR(100) | |
| `zoning_type` | VARCHAR(100) | |
| `boundary` | GEOGRAPHY(POLYGON, 4326) | GIST — future polygon search |
| `created_at` | TIMESTAMPTZ | |
| `updated_at` | TIMESTAMPTZ | |

---

### `property_buildings`

| Column | Type |
|--------|------|
| `id` | UUID PK |
| `property_id` | UUID FK UNIQUE |
| `construction_year` | SMALLINT |
| `building_age` | SMALLINT (generated or computed) |
| `floor_count` | SMALLINT |
| `floor_number` | SMALLINT |
| `unit_number` | VARCHAR(50) |
| `net_area_sqm` | NUMERIC(12,2) |
| `gross_area_sqm` | NUMERIC(12,2) |
| `room_count` | NUMERIC(4,1) |
| `living_room_count` | SMALLINT |
| `bedroom_count` | SMALLINT |
| `bathroom_count` | SMALLINT |
| `balcony_count` | SMALLINT |
| `parking_count` | SMALLINT |
| `created_at`, `updated_at` | TIMESTAMPTZ |

---

### `property_features`

| Column | Type |
|--------|------|
| `id` | UUID PK |
| `property_id` | UUID FK UNIQUE |
| `heating_type` | VARCHAR(50) |
| `cooling_type` | VARCHAR(50) |
| `energy_certificate_class` | CHAR(1) |
| `has_elevator` | BOOLEAN |
| `has_parking` | BOOLEAN |
| `has_balcony` | BOOLEAN |
| `has_garden` | BOOLEAN |
| `has_pool` | BOOLEAN |
| `has_security` | BOOLEAN |
| `has_storage` | BOOLEAN |
| `has_smart_home` | BOOLEAN |
| `has_solar` | BOOLEAN |
| `has_ev_charger` | BOOLEAN |
| `accessibility_level` | VARCHAR(30) |
| `created_at`, `updated_at` | TIMESTAMPTZ |

---

### `property_amenities`

| Column | Type | Constraints |
|--------|------|-------------|
| `id` | UUID PK | |
| `property_id` | UUID | FK → properties |
| `amenity_code` | VARCHAR(50) | FK → amenity_definitions |
| `value` | VARCHAR(200) | Optional qualifier |
| `created_at` | TIMESTAMPTZ | |

**UNIQUE** `(property_id, amenity_code)`

---

### `property_images`

| Column | Type |
|--------|------|
| `id` | UUID PK |
| `property_id` | UUID FK INDEX |
| `storage_key` | VARCHAR(500) |
| `url` | VARCHAR(1000) |
| `thumbnail_url` | VARCHAR(1000) |
| `caption` | VARCHAR(500) |
| `sort_order` | SMALLINT DEFAULT 0 |
| `is_primary` | BOOLEAN DEFAULT FALSE |
| `width`, `height` | INTEGER |
| `file_size` | BIGINT |
| `mime_type` | VARCHAR(100) |
| `processing_status` | VARCHAR(20) DEFAULT 'pending' |
| `created_at`, `updated_at` | TIMESTAMPTZ |
| `deleted_at` | TIMESTAMPTZ |

---

### `property_videos`

Same structure as images plus: `video_type`, `duration_seconds`, `embed_url`, `provider`.

---

### `property_documents`

| Column | Type |
|--------|------|
| `id` | UUID PK |
| `property_id` | UUID FK INDEX |
| `document_type` | VARCHAR(50) NOT NULL |
| `storage_key` | VARCHAR(500) |
| `url` | VARCHAR(1000) |
| `file_name` | VARCHAR(255) |
| `mime_type` | VARCHAR(100) |
| `file_size` | BIGINT |
| `verified` | BOOLEAN DEFAULT FALSE |
| `verified_at` | TIMESTAMPTZ |
| `verified_by` | UUID |
| `created_at`, `updated_at` | TIMESTAMPTZ |
| `deleted_at` | TIMESTAMPTZ |

---

### `property_ownership`

| Column | Type |
|--------|------|
| `id` | UUID PK |
| `property_id` | UUID FK INDEX |
| `owner_type` | VARCHAR(30) |
| `owner_name` | VARCHAR(255) |
| `owner_external_id` | UUID |
| `ownership_percentage` | NUMERIC(5,2) |
| `acquired_at` | DATE |
| `released_at` | DATE |
| `is_current` | BOOLEAN DEFAULT TRUE |
| `created_at`, `updated_at` | TIMESTAMPTZ |

---

### `property_tags`

| Column | Type |
|--------|------|
| `id` | UUID PK |
| `property_id` | UUID FK |
| `tag` | VARCHAR(100) |
| `created_at` | TIMESTAMPTZ |

**UNIQUE** `(property_id, tag)`

---

### `property_metadata`

| Column | Type |
|--------|------|
| `id` | UUID PK |
| `property_id` | UUID FK UNIQUE |
| `metadata` | JSONB DEFAULT '{}' |
| `tenant_extensions` | JSONB DEFAULT '{}' |
| `schema_version` | VARCHAR(20) DEFAULT '1.0' |
| `created_at`, `updated_at` | TIMESTAMPTZ |

**GIN index** on `metadata` for JSONB queries.

---

### `property_external_sources`

| Column | Type |
|--------|------|
| `id` | UUID PK |
| `property_id` | UUID FK INDEX |
| `source_type` | VARCHAR(30) NOT NULL |
| `source_reference` | TEXT |
| `source_payload` | JSONB |
| `imported_at` | TIMESTAMPTZ |
| `created_at` | TIMESTAMPTZ |

---

### `property_listings`

| Column | Type |
|--------|------|
| `id` | UUID PK |
| `property_id` | UUID FK UNIQUE |
| `original_url` | TEXT |
| `provider` | VARCHAR(50) |
| `listing_id` | VARCHAR(100) |
| `listing_date` | DATE |
| `last_synced_at` | TIMESTAMPTZ |
| `sync_status` | VARCHAR(20) |
| `provider_metadata` | JSONB |
| `created_at`, `updated_at` | TIMESTAMPTZ |

**UNIQUE** `(provider, listing_id)` — prevent duplicate imports.

---

### History Tables

#### `property_price_history`

| Column | Type |
|--------|------|
| `id` | UUID PK |
| `property_id` | UUID FK INDEX |
| `price_type` | VARCHAR(20) — sale/rental/maintenance |
| `old_amount` | NUMERIC(18,2) |
| `new_amount` | NUMERIC(18,2) |
| `currency` | CHAR(3) |
| `changed_at` | TIMESTAMPTZ DEFAULT now() |
| `changed_by` | UUID |
| `change_reason` | VARCHAR(200) |

#### `property_status_history`

| Column | Type |
|--------|------|
| `id` | UUID PK |
| `property_id` | UUID FK INDEX |
| `old_status` | VARCHAR(30) |
| `new_status` | VARCHAR(30) |
| `changed_at` | TIMESTAMPTZ |
| `changed_by` | UUID |
| `reason` | TEXT |

#### `property_ownership_history`

Snapshot on ownership changes (same fields as ownership + `effective_from`, `effective_to`).

---

### `property_versions`

| Column | Type |
|--------|------|
| `id` | UUID PK |
| `property_id` | UUID FK INDEX |
| `version_number` | INTEGER |
| `snapshot` | JSONB NOT NULL |
| `change_summary` | TEXT |
| `created_at` | TIMESTAMPTZ |
| `created_by` | UUID |

**UNIQUE** `(property_id, version_number)`

---

### `property_audit_logs`

Append-only audit trail.

| Column | Type |
|--------|------|
| `id` | UUID PK |
| `property_id` | UUID INDEX |
| `tenant_id` | UUID INDEX |
| `action` | VARCHAR(50) |
| `actor_id` | UUID |
| `actor_type` | VARCHAR(20) — user/system/api_key |
| `changes` | JSONB |
| `ip_address` | INET |
| `user_agent` | TEXT |
| `correlation_id` | UUID |
| `created_at` | TIMESTAMPTZ DEFAULT now() |

**Partition candidate** — range partition by `created_at` (monthly).

---

### `outbox_events`

Transactional outbox for reliable event publishing.

| Column | Type |
|--------|------|
| `id` | UUID PK |
| `aggregate_id` | UUID INDEX |
| `aggregate_type` | VARCHAR(50) |
| `event_type` | VARCHAR(100) |
| `payload` | JSONB NOT NULL |
| `metadata` | JSONB |
| `status` | VARCHAR(20) DEFAULT 'pending' |
| `created_at` | TIMESTAMPTZ |
| `published_at` | TIMESTAMPTZ |
| `retry_count` | SMALLINT DEFAULT 0 |

---

### Lookup Tables

#### `property_types`

| Column | Type |
|--------|------|
| `code` | VARCHAR(50) PK |
| `category` | VARCHAR(50) |
| `display_name` | JSONB — i18n |
| `is_active` | BOOLEAN |
| `sort_order` | SMALLINT |

#### `amenity_definitions`

| Column | Type |
|--------|------|
| `code` | VARCHAR(50) PK |
| `category` | VARCHAR(50) |
| `display_name` | JSONB |
| `value_type` | VARCHAR(20) — boolean/enum/text |
| `is_active` | BOOLEAN |

---

## Cross-Cutting Concerns

### Soft Delete

All user-facing entities include `deleted_at TIMESTAMPTZ`. Queries default to `WHERE deleted_at IS NULL`. Partial indexes exclude deleted rows.

### Optimistic Locking

`properties.version` incremented on every update. Application checks `WHERE id = :id AND version = :expected_version`.

### Auditing

- `created_at`, `updated_at`, `created_by`, `updated_by` on mutable tables
- `property_audit_logs` for full change history
- Database triggers optional for `updated_at` auto-update

### Full-Text Search

```sql
-- Trigger to maintain search_vector
NEW.search_vector :=
  setweight(to_tsvector('simple', coalesce(NEW.title, '')), 'A') ||
  setweight(to_tsvector('simple', coalesce(NEW.description, '')), 'B') ||
  setweight(to_tsvector('simple', coalesce(NEW.province, '') || ' ' || coalesce(NEW.district, '') || ' ' || coalesce(NEW.neighborhood, '')), 'C');
```

Support `turkish` and `english` configs via separate vectors in Phase 2.

### Partitioning Strategy (Future)

| Table | Strategy | Key |
|-------|----------|-----|
| `properties` | Hash by `tenant_id` | Enterprise scale |
| `property_audit_logs` | Range by `created_at` | Monthly |
| `outbox_events` | Range by `created_at` | Weekly, with purge |
| `property_price_history` | Range by `changed_at` | Yearly |

### Row-Level Security (Optional Enterprise)

```sql
ALTER TABLE property.properties ENABLE ROW LEVEL SECURITY;
CREATE POLICY tenant_isolation ON property.properties
  USING (tenant_id = current_setting('app.current_tenant_id')::UUID);
```

---

## Migration Strategy

1. Alembic autogenerate disabled — all migrations hand-written
2. Numbered revisions: `001_initial_schema`, `002_add_postgis`, etc.
3. Zero-downtime migrations: add column → backfill → switch → drop old
4. Seed data migrations for lookup tables in separate revision
