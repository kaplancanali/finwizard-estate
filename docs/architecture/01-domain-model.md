# 1. Domain Model

## Bounded Context

**Property Management Context** — owns the lifecycle, metadata, media references, ownership records, and search projections of real estate assets.

### Context Map (Relationships)

| Context | Relationship | Integration |
|---------|--------------|-------------|
| Identity & Access | Customer-Supplier | JWT claims, user/tenant IDs |
| Valuation Service | Published Language | Consumes `PropertyPriceChanged` events |
| Risk Service | Published Language | Consumes `PropertyLocationChanged` events |
| Listing Ingestion | Anti-Corruption Layer | External listing adapters → domain |
| Search Index (future ES) | Conformist | Consumes domain events for index sync |
| Notification Service | Event Consumer | Property status/ownership changes |

---

## Ubiquitous Language

| Term | Definition |
|------|------------|
| **Property** | A real estate asset identified by UUID, with full metadata lifecycle |
| **Property Code** | Human-readable unique identifier (e.g., `FW-TR-IST-00001234`) |
| **Listing** | External marketplace reference linked to a property |
| **Parcel** | Cadastral land record (block, parcel number, area) |
| **Source** | Origin of property creation (manual, URL, coordinates, etc.) |
| **Version** | Immutable snapshot of property state at a point in time |
| **Tenant** | Enterprise customer organization owning a subset of properties |

---

## Aggregates

### Aggregate Root: `Property`

The Property aggregate is the consistency boundary. All mutations flow through the aggregate root.

```
Property (Aggregate Root)
├── PropertyIdentity        [Value Object]
├── PropertyClassification  [Value Object]
├── PropertyPricing         [Entity]
├── PropertyLocation        [Entity]
├── PropertyParcel          [Entity - optional]
├── PropertyBuilding        [Entity - optional]
├── PropertyFeatures        [Entity]
├── PropertyAmenities       [Collection Entity]
├── PropertyMedia           [Collection - Images, Videos, Tours]
├── PropertyDocuments       [Collection Entity]
├── PropertyListing         [Entity - optional]
├── PropertyOwnership       [Collection Entity]
├── PropertyTags            [Collection Entity]
├── PropertyMetadata        [Entity - extensible JSONB]
├── PropertyExternalSource  [Entity]
├── PropertyVersion         [Entity - snapshots]
└── PropertyAuditLog        [Entity - append-only]
```

#### Invariants (Aggregate Rules)

1. A property must have at least one address OR valid coordinates
2. `property_code` is immutable after creation
3. `slug` is unique per tenant (globally unique for platform properties)
4. Status transitions follow defined state machine (see below)
5. Price changes append to `PropertyPriceHistory`; never mutate history
6. Soft-deleted properties cannot be updated (only restored)
7. Optimistic lock: `version` must match on every update
8. Media and documents store references (URLs/keys), not binary in DB

#### Status State Machine

```
                    ┌──────────┐
         ┌─────────│  DRAFT   │─────────┐
         │         └────┬─────┘         │
         │              │ submit       │ discard
         │              ▼              ▼
         │         ┌──────────┐   ┌──────────┐
         │         │ PENDING  │   │ ARCHIVED │
         │         └────┬─────┘   └──────────┘
         │              │ approve
         │              ▼
         │         ┌──────────┐
    ┌────┤         │  ACTIVE  │◄────────────┐
    │    │         └────┬─────┘             │
    │    │    list/delist│                  │ restore
    │    │              ▼                   │
    │    │         ┌──────────┐              │
    │    └────────►│  LISTED  │──────────────┤
    │              └────┬─────┘              │
    │                   │ sold/withdrawn     │
    │                   ▼                    │
    │              ┌──────────┐              │
    └──────────────│ INACTIVE │──────────────┘
                   └────┬─────┘
                        │ delete (soft)
                        ▼
                   ┌──────────┐
                   │ DELETED  │
                   └──────────┘
```

---

## Entities

### Property (Root)

| Field Group | Attributes |
|-------------|------------|
| Identity | `id` (UUID), `tenant_id`, `property_code`, `slug` |
| Basic | `title`, `description`, `summary` |
| Classification | `type`, `category`, `subtype` |
| Status | `status`, `visibility`, `published_at` |
| Concurrency | `version`, `created_at`, `updated_at`, `deleted_at` |
| Audit | `created_by`, `updated_by` |

### PropertyPricing

| Field | Type | Notes |
|-------|------|-------|
| `sale_price` | Decimal | Nullable |
| `rental_price` | Decimal | Nullable |
| `maintenance_fee` | Decimal | Nullable |
| `currency` | ISO 4217 | Required if any price set |
| `price_on_request` | bool | |
| `price_per_sqm` | Decimal | Computed, denormalized for search |

### PropertyLocation / PropertyAddress

| Field | Type | Notes |
|-------|------|-------|
| `country_code` | ISO 3166-1 alpha-2 | Required |
| `province` | string | |
| `district` | string | |
| `neighborhood` | string | |
| `street` | string | |
| `postal_code` | string | |
| `address_line` | string | Full formatted address |
| `latitude` | Decimal(9,6) | |
| `longitude` | Decimal(9,6) | |
| `elevation` | Decimal | Meters |
| `location` | Geography(POINT) | PostGIS — derived from lat/lng |
| `geohash` | string | For proximity bucketing |
| `timezone` | string | IANA |

### PropertyParcel

| Field | Type |
|-------|------|
| `block` | string |
| `parcel_number` | string |
| `parcel_area_sqm` | Decimal |
| `cadastral_reference` | string |
| `zoning_type` | string |

### PropertyBuilding

| Field | Type |
|-------|------|
| `construction_year` | int |
| `building_age` | int (computed) |
| `floor_count` | int |
| `floor_number` | int |
| `unit_number` | string |
| `net_area_sqm` | Decimal |
| `gross_area_sqm` | Decimal |
| `room_count` | Decimal (supports 2.5 rooms) |
| `living_room_count` | int |
| `bedroom_count` | int |
| `bathroom_count` | int |
| `balcony_count` | int |
| `parking_count` | int |

### PropertyFeatures (Boolean / Enum flags)

`heating_type`, `cooling_type`, `energy_certificate_class`, `has_elevator`, `has_parking`, `has_balcony`, `has_garden`, `has_pool`, `has_security`, `has_storage`, `has_smart_home`, `has_solar`, `has_ev_charger`, `accessibility_level`

### PropertyAmenity

| Field | Type |
|-------|------|
| `amenity_code` | FK → amenity lookup |
| `value` | string (optional qualifier) |

### PropertyImage

| Field | Type |
|-------|------|
| `id` | UUID |
| `storage_key` | string |
| `url` | string |
| `thumbnail_url` | string |
| `caption` | string |
| `sort_order` | int |
| `is_primary` | bool |
| `width`, `height` | int |
| `mime_type` | string |
| `processing_status` | enum |

### PropertyVideo / PropertyTour

Similar structure with `video_url`, `tour_type` (360, virtual, walkthrough), `provider`, `embed_url`.

### PropertyDocument

| Field | Type |
|-------|------|
| `document_type` | enum (deed, building_permit, occupancy_permit, energy_cert, other) |
| `storage_key`, `url` | string |
| `file_name`, `mime_type`, `file_size` | |
| `verified` | bool |
| `verified_at`, `verified_by` | |

### PropertyListing

| Field | Type |
|-------|------|
| `original_url` | string |
| `provider` | enum (sahibinden, emlakjet, hepsiemlak, custom) |
| `listing_id` | string |
| `listing_date` | date |
| `last_synced_at` | datetime |
| `sync_status` | enum |

### PropertyOwnership

| Field | Type |
|-------|------|
| `owner_type` | enum (individual, company, trust) |
| `owner_name` | string |
| `owner_id` | UUID (FK to identity service, optional) |
| `ownership_percentage` | Decimal |
| `acquired_at` | date |
| `released_at` | date (nullable) |
| `is_current` | bool |

### PropertyExternalSource

| Field | Type |
|-------|------|
| `source_type` | enum (manual, listing_url, address, coordinates, map_selection, parcel, ocr, voice) |
| `source_reference` | string |
| `source_payload` | JSONB |
| `imported_at` | datetime |

### PropertyVersion

Immutable snapshot: full property JSON at version N, triggered on significant changes.

### PropertyAuditLog

Append-only: `action`, `actor_id`, `actor_type`, `changes` (JSONB diff), `ip_address`, `correlation_id`.

---

## Value Objects

```python
# Design references — not implementation

@dataclass(frozen=True)
class PropertyCode:
    value: str  # Pattern: FW-{COUNTRY}-{REGION}-{SEQUENCE}

@dataclass(frozen=True)
class Slug:
    value: str  # URL-safe, unique per tenant

@dataclass(frozen=True)
class GeoCoordinate:
    latitude: Decimal   # -90 to 90
    longitude: Decimal  # -180 to 180
    elevation: Decimal | None

@dataclass(frozen=True)
class Money:
    amount: Decimal
    currency: str  # ISO 4217

@dataclass(frozen=True)
class Area:
    value_sqm: Decimal

@dataclass(frozen=True)
class PropertyClassification:
    type: PropertyType      # apartment, villa, land, ...
    category: PropertyCategory  # residential, commercial, industrial, land
    subtype: str | None     # extensible
```

---

## Enumerations

### PropertyType (extensible via lookup table)

`apartment`, `villa`, `residence`, `detached_house`, `land`, `commercial`, `office`, `store`, `warehouse`, `factory`, `hotel`, `farm`, `mixed_project`, `industrial`, `other`

### PropertyCategory

`residential`, `commercial`, `industrial`, `land`, `mixed_use`, `hospitality`, `agricultural`

### PropertyStatus

`draft`, `pending`, `active`, `listed`, `inactive`, `archived`, `deleted`

### PropertyVisibility

`private`, `tenant`, `public`, `partner`

### SourceType

`manual`, `listing_url`, `address`, `coordinates`, `map_selection`, `parcel`, `ocr`, `voice`

### DocumentType

`property_deed`, `building_permit`, `occupancy_permit`, `energy_certificate`, `floor_plan`, `other`

---

## Domain Events

Raised by aggregate root; persisted to outbox table.

| Event | Trigger |
|-------|---------|
| `PropertyCreated` | New property registered |
| `PropertyUpdated` | Any field change |
| `PropertyDeleted` | Soft delete |
| `PropertyRestored` | Undelete |
| `PropertyImported` | Bulk import completed |
| `PropertyPriceChanged` | Sale/rental price mutation |
| `PropertyLocationChanged` | Address or coordinates change |
| `PropertyStatusChanged` | Status transition |
| `PropertyImagesUpdated` | Image add/remove/reorder |
| `PropertyDocumentsUpdated` | Document add/remove |
| `PropertyOwnershipChanged` | Ownership record mutation |
| `PropertyListed` | Linked to external listing |
| `PropertyVersionCreated` | Snapshot created |

---

## Domain Services

| Service | Responsibility |
|---------|----------------|
| `PropertyCodeGenerator` | Generate unique property codes per tenant/region |
| `SlugGenerator` | Generate and deduplicate URL slugs |
| `PropertyValidator` | Cross-field validation (area vs rooms, year vs age) |
| `GeocodingService` (interface) | Address ↔ coordinates (implemented in infra) |
| `PropertySearchDomainService` | Complex filter composition rules |
| `PropertyMergeService` | Deduplication when same parcel/listing detected |

---

## Factory

`PropertyFactory` — creates property from source type:

- `create_from_manual(data)`
- `create_from_listing_url(url)`
- `create_from_address(address)`
- `create_from_coordinates(lat, lng)`
- `create_from_map_selection(geojson)`
- `create_from_parcel(parcel_info)`

Each factory method sets `PropertyExternalSource` and raises appropriate domain events.

---

## Specifications (Query-side domain rules)

| Specification | Purpose |
|---------------|---------|
| `ActivePropertySpec` | status IN (active, listed) AND deleted_at IS NULL |
| `TenantPropertySpec` | tenant_id = :tenant |
| `WithinRadiusSpec` | ST_DWithin(location, point, radius) |
| `WithinPolygonSpec` | ST_Within(location, polygon) |
| `WithinBoundingBoxSpec` | lat/lng bounds |
| `PriceRangeSpec` | sale_price BETWEEN min AND max |

---

## Extensibility Strategy

1. **Property types** — `property_types` lookup table; new types added without migration
2. **Amenities** — `amenity_definitions` lookup with categories:category tags
3. **Metadata** — `property_metadata.metadata` JSONB with JSON Schema validation per type
4. **Source types** — enum extensible via `ALTER TYPE ... ADD VALUE` or lookup table migration
5. **Custom fields** — tenant-specific fields in `property_metadata.tenant_extensions` JSONB
