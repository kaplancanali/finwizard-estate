# 9. DTO Design

DTOs are organized by layer. **Presentation schemas** (Pydantic) are separate from **application DTOs** (dataclasses) to prevent API coupling to domain.

---

## Layer Mapping

```
HTTP Request
    ↓  (Pydantic validation)
Presentation Schema (schemas/)
    ↓  (mapper)
Application DTO (application/dto/)
    ↓  (use case)
Domain Entity (domain/)
    ↓  (mapper)
ORM Model (infrastructure/)
```

---

## Presentation Schemas (Pydantic v2)

### PropertyCreateRequest

```python
class PricingInput(BaseModel):
    sale_price: Decimal | None = Field(None, ge=0, decimal_places=2)
    rental_price: Decimal | None = Field(None, ge=0, decimal_places=2)
    maintenance_fee: Decimal | None = Field(None, ge=0, decimal_places=2)
    currency: str = Field("TRY", min_length=3, max_length=3)
    price_on_request: bool = False

class LocationInput(BaseModel):
    country_code: str = Field(..., min_length=2, max_length=2)
    province: str | None = Field(None, max_length=100)
    district: str | None = Field(None, max_length=100)
    neighborhood: str | None = Field(None, max_length=200)
    street: str | None = Field(None, max_length=300)
    postal_code: str | None = Field(None, max_length=20)
    address_line: str | None = None
    latitude: Decimal | None = Field(None, ge=-90, le=90)
    longitude: Decimal | None = Field(None, ge=-180, le=180)
    elevation: Decimal | None = None

    @model_validator(mode="after")
    def validate_location(self) -> Self:
        has_coords = self.latitude is not None and self.longitude is not None
        has_address = any([self.province, self.district, self.address_line])
        if not has_coords and not has_address:
            raise ValueError("Either coordinates or address components required")
        return self

class BuildingInput(BaseModel):
    construction_year: int | None = Field(None, ge=1800, le=2100)
    floor_count: int | None = Field(None, ge=0)
    floor_number: int | None = None
    unit_number: str | None = Field(None, max_length=50)
    net_area_sqm: Decimal | None = Field(None, gt=0)
    gross_area_sqm: Decimal | None = Field(None, gt=0)
    room_count: Decimal | None = Field(None, gt=0)
    living_room_count: int | None = Field(None, ge=0)
    bedroom_count: int | None = Field(None, ge=0)
    bathroom_count: int | None = Field(None, ge=0)
    balcony_count: int | None = Field(None, ge=0)
    parking_count: int | None = Field(None, ge=0)

class FeaturesInput(BaseModel):
    heating_type: str | None = None
    cooling_type: str | None = None
    energy_certificate_class: str | None = Field(None, max_length=1)
    has_elevator: bool = False
    has_parking: bool = False
    has_balcony: bool = False
    has_garden: bool = False
    has_pool: bool = False
    has_security: bool = False
    has_storage: bool = False
    has_smart_home: bool = False
    has_solar: bool = False
    has_ev_charger: bool = False
    accessibility_level: str | None = None

class SourceInput(BaseModel):
    source_type: SourceType
    source_reference: str | None = None
    source_payload: dict | None = None

class PropertyCreateRequest(BaseModel):
    title: str = Field(..., min_length=3, max_length=500)
    description: str | None = Field(None, max_length=10000)
    property_type: PropertyType
    property_category: PropertyCategory
    property_subtype: str | None = Field(None, max_length=100)
    status: PropertyStatus = PropertyStatus.DRAFT
    visibility: PropertyVisibility = PropertyVisibility.PRIVATE
    pricing: PricingInput | None = None
    location: LocationInput
    parcel: ParcelInput | None = None
    building: BuildingInput | None = None
    features: FeaturesInput | None = None
    amenities: list[str] = Field(default_factory=list)
    tags: list[str] = Field(default_factory=list, max_length=20)
    source: SourceInput = Field(default_factory=lambda: SourceInput(source_type=SourceType.MANUAL))
```

### PropertyUpdateRequest (PATCH)

```python
class PropertyUpdateRequest(BaseModel):
    version: int = Field(..., ge=1)
    title: str | None = Field(None, min_length=3, max_length=500)
    description: str | None = None
    pricing: PricingInput | None = None
    location: LocationInput | None = None
    building: BuildingInput | None = None
    features: FeaturesInput | None = None
    amenities: list[str] | None = None
    tags: list[str] | None = None
```

### PropertyResponse

```python
class PropertyResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    tenant_id: UUID
    property_code: str
    slug: str
    title: str
    description: str | None
    property_type: PropertyType
    property_category: PropertyCategory
    property_subtype: str | None
    status: PropertyStatus
    visibility: PropertyVisibility
    pricing: PricingResponse | None
    location: LocationResponse
    parcel: ParcelResponse | None
    building: BuildingResponse | None
    features: FeaturesResponse | None
    amenities: list[str]
    tags: list[str]
    images: list[ImageResponse] | None = None
    documents: list[DocumentResponse] | None = None
    listing: ListingResponse | None = None
    ownership: list[OwnershipResponse] | None = None
    metadata: dict | None = None
    version: int
    published_at: datetime | None
    created_at: datetime
    updated_at: datetime
    created_by: UUID
    updated_by: UUID | None
```

### PropertySummaryResponse (search results)

Lightweight projection — no nested collections.

```python
class PropertySummaryResponse(BaseModel):
    id: UUID
    property_code: str
    slug: str
    title: str
    property_type: PropertyType
    status: PropertyStatus
    sale_price: Decimal | None
    rental_price: Decimal | None
    currency: str | None
    province: str | None
    district: str | None
    neighborhood: str | None
    latitude: Decimal | None
    longitude: Decimal | None
    net_area_sqm: Decimal | None
    room_count: Decimal | None
    bathroom_count: int | None
    primary_image_url: str | None
    distance_meters: float | None = None
    created_at: datetime
```

---

## Search Schemas

```python
class RangeFilter(BaseModel):
    min: Decimal | int | None = None
    max: Decimal | int | None = None

class GeoRadiusFilter(BaseModel):
    type: Literal["radius"] = "radius"
    latitude: Decimal = Field(..., ge=-90, le=90)
    longitude: Decimal = Field(..., ge=-180, le=180)
    radius_meters: int = Field(..., gt=0, le=100_000)

class GeoBoundingBoxFilter(BaseModel):
    type: Literal["bounding_box"] = "bounding_box"
    north: Decimal
    south: Decimal
    east: Decimal
    west: Decimal

class GeoPolygonFilter(BaseModel):
    type: Literal["polygon"] = "polygon"
    coordinates: list[list[Decimal]]  # [[lng, lat], ...]

GeoFilter = GeoRadiusFilter | GeoBoundingBoxFilter | GeoPolygonFilter

class SearchFilters(BaseModel):
    property_types: list[PropertyType] | None = None
    property_categories: list[PropertyCategory] | None = None
    status: list[PropertyStatus] | None = None
    sale_price: RangeFilter | None = None
    rental_price: RangeFilter | None = None
    net_area_sqm: RangeFilter | None = None
    room_count: RangeFilter | None = None
    bathroom_count: RangeFilter | None = None
    construction_year: RangeFilter | None = None
    country_code: str | None = None
    provinces: list[str] | None = None
    districts: list[str] | None = None
    heating_types: list[str] | None = None
    amenities: list[str] | None = None
    features: dict[str, bool] | None = None
    tags: list[str] | None = None

class SortField(BaseModel):
    field: str
    direction: Literal["asc", "desc"] = "asc"

class PropertySearchRequest(BaseModel):
    query: str | None = Field(None, max_length=500)
    filters: SearchFilters | None = None
    geo: GeoFilter | None = None
    sort: list[SortField] = Field(default_factory=lambda: [SortField(field="created_at", direction="desc")])
    pagination: PaginationInput = Field(default_factory=PaginationInput)
    include_facets: bool = False
```

---

## Bulk Operation Schemas

```python
class BulkImportRequest(BaseModel):
    source_type: SourceType
    items: list[BulkImportItem] = Field(..., min_length=1, max_length=500)
    options: BulkImportOptions = Field(default_factory=BulkImportOptions)

class BulkImportOptions(BaseModel):
    async_mode: bool = Field(True, alias="async")
    skip_duplicates: bool = True
    default_status: PropertyStatus = PropertyStatus.DRAFT
    auto_geocode: bool = True

class BulkJobResponse(BaseModel):
    job_id: UUID
    status: Literal["queued", "processing", "completed", "failed"]
    total_items: int
    processed: int = 0
    created: int = 0
    skipped: int = 0
    failed: int = 0
    errors: list[BulkError] = Field(default_factory=list)
    started_at: datetime | None = None
    completed_at: datetime | None = None
```

---

## Media Schemas

```python
class ImageUploadRequest(BaseModel):
    file_name: str = Field(..., max_length=255)
    mime_type: str = Field(..., pattern=r"^image/(jpeg|png|webp|gif)$")
    file_size: int = Field(..., gt=0, le=20_971_520)  # 20MB max
    caption: str | None = Field(None, max_length=500)
    is_primary: bool = False
    sort_order: int = 0

class ImageUploadResponse(BaseModel):
    image: ImageResponse
    upload_url: str
    expires_at: datetime

class DocumentUploadRequest(BaseModel):
    file_name: str
    mime_type: str
    file_size: int = Field(..., le=52_428_800)  # 50MB max
    document_type: DocumentType
```

---

## Common Schemas

```python
class PaginationInput(BaseModel):
    page: int = Field(1, ge=1)
    page_size: int = Field(20, ge=1, le=100)

class PaginationMeta(BaseModel):
    page: int
    page_size: int
    total_items: int
    total_pages: int
    has_next: bool
    has_previous: bool

class ApiResponse(BaseModel, Generic[T]):
    data: T
    meta: ResponseMeta

class PaginatedResponse(BaseModel, Generic[T]):
    data: list[T]
    pagination: PaginationMeta
    meta: ResponseMeta

class ErrorDetail(BaseModel):
    field: str | None = None
    message: str
    code: str | None = None

class ErrorResponse(BaseModel):
    error: ErrorBody

class ErrorBody(BaseModel):
    code: str
    message: str
    details: list[ErrorDetail] = Field(default_factory=list)
    correlation_id: str
```

---

## Application DTOs (dataclasses)

Internal to application layer — not exposed via API.

```python
@dataclass
class CreatePropertyDTO:
    tenant_id: UUID
    created_by: UUID
    title: str
    property_type: PropertyType
    property_category: PropertyCategory
  # ... flattened from presentation schema

@dataclass
class PropertySearchCriteria:
    tenant_id: UUID
    query: str | None
    filters: SearchFilterSet
    geo: GeoCriteria | None
    sort: list[SortCriteria]
    page: int
    page_size: int
    include_facets: bool

@dataclass
class PropertySearchResult:
    items: list[PropertySummary]
    total: int
    facets: dict[str, dict] | None
    page: int
    page_size: int
```

---

## Mapping Rules

| From | To | Mapper Location |
|------|----|-----------------|
| `PropertyCreateRequest` | `CreatePropertyDTO` | `presentation/mappers/request_mappers.py` |
| `CreatePropertyDTO` | `Property` (domain) | `application/mappers/domain_mappers.py` |
| `Property` (domain) | `PropertyResponse` | `presentation/mappers/response_mappers.py` |
| `Property` (domain) | ORM models | `infrastructure/persistence/mappers/property_mapper.py` |
| ORM models | `PropertySummary` | `infrastructure/persistence/mappers/search_mapper.py` |

**Rule:** Presentation layer never imports domain entities. Application layer never imports presentation schemas.
