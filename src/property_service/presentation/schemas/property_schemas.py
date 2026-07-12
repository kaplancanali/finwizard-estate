from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator
from typing_extensions import Self

from property_service.config.lookup_codes import KNOWN_AMENITY_CODES
from property_service.domain.enums.document_type import DocumentType
from property_service.domain.enums.property_category import PropertyCategory
from property_service.domain.enums.property_status import PropertyStatus
from property_service.domain.enums.property_type import PropertyType
from property_service.domain.enums.property_visibility import PropertyVisibility
from property_service.domain.enums.source_type import SourceType
from property_service.presentation.schemas.field_validators import (
    strip_non_empty_title,
    validate_construction_year,
    validate_decimal_places,
    validate_iso_country_code,
    validate_iso_currency,
    validate_price_digits,
    validate_room_count_increment,
    validate_tag_lengths,
)


class PricingInput(BaseModel):
    sale_price: Decimal | None = Field(None, ge=0)
    rental_price: Decimal | None = Field(None, ge=0)
    maintenance_fee: Decimal | None = Field(None, ge=0)
    currency: str = Field("TRY", min_length=3, max_length=3)
    price_on_request: bool = False

    @field_validator("currency")
    @classmethod
    def validate_currency(cls, value: str) -> str:
        return validate_iso_currency(value)

    @field_validator("sale_price")
    @classmethod
    def validate_sale_price(cls, value: Decimal | None) -> Decimal | None:
        if value is not None:
            return validate_price_digits(value)
        return value


PricingSchema = PricingInput
PricingResponse = PricingInput


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

    @field_validator("country_code")
    @classmethod
    def validate_country(cls, value: str) -> str:
        return validate_iso_country_code(value)

    @field_validator("latitude", "longitude")
    @classmethod
    def validate_coordinate_precision(cls, value: Decimal | None) -> Decimal | None:
        if value is not None:
            return validate_decimal_places(value, max_places=6)
        return value

    @model_validator(mode="after")
    def validate_location(self) -> Self:
        has_coords = self.latitude is not None and self.longitude is not None
        has_address = any([self.province, self.district, self.address_line])
        if not has_coords and not has_address:
            raise ValueError("Either coordinates or address components required")
        return self


LocationSchema = LocationInput
LocationResponse = LocationInput


class ParcelInput(BaseModel):
    block: str | None = Field(None, max_length=50)
    parcel_number: str | None = Field(None, max_length=50)
    parcel_area_sqm: Decimal | None = Field(None, gt=0)
    cadastral_reference: str | None = Field(None, max_length=100)
    zoning_type: str | None = Field(None, max_length=100)


ParcelResponse = ParcelInput


class BuildingInput(BaseModel):
    construction_year: int | None = Field(None, ge=1800)
    floor_count: int | None = Field(None, ge=0)
    floor_number: int | None = None
    unit_number: str | None = Field(None, max_length=50)
    net_area_sqm: Decimal | None = Field(None, gt=0, le=Decimal("999999.99"))
    gross_area_sqm: Decimal | None = Field(None, gt=0)
    room_count: Decimal | None = Field(None, gt=0)
    living_room_count: int | None = Field(None, ge=0)
    bedroom_count: int | None = Field(None, ge=0)
    bathroom_count: int | None = Field(None, ge=0)
    balcony_count: int | None = Field(None, ge=0)
    parking_count: int | None = Field(None, ge=0)

    @field_validator("construction_year")
    @classmethod
    def validate_year(cls, value: int | None) -> int | None:
        if value is not None:
            return validate_construction_year(value)
        return value

    @field_validator("room_count")
    @classmethod
    def validate_rooms(cls, value: Decimal | None) -> Decimal | None:
        if value is not None:
            return validate_room_count_increment(value)
        return value


BuildingSchema = BuildingInput
BuildingResponse = BuildingInput


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


FeaturesSchema = FeaturesInput
FeaturesResponse = FeaturesInput


class SourceInput(BaseModel):
    source_type: SourceType = SourceType.MANUAL
    source_reference: str | None = None
    source_payload: dict | None = None


SourceSchema = SourceInput


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
    source: SourceInput = Field(default_factory=SourceInput)

    @field_validator("title")
    @classmethod
    def validate_title(cls, value: str) -> str:
        return strip_non_empty_title(value)

    @field_validator("tags")
    @classmethod
    def validate_tags(cls, value: list[str]) -> list[str]:
        return validate_tag_lengths(value)

    @field_validator("amenities")
    @classmethod
    def validate_amenities(cls, value: list[str]) -> list[str]:
        unknown = sorted(set(value) - KNOWN_AMENITY_CODES)
        if unknown:
            raise ValueError(f"Unknown amenities: {', '.join(unknown)}")
        return value


class PropertyUpdateRequest(BaseModel):
    version: int = Field(..., ge=1)
    title: str | None = Field(None, min_length=3, max_length=500)
    description: str | None = Field(None, max_length=10000)
    pricing: PricingInput | None = None
    location: LocationInput | None = None
    parcel: ParcelInput | None = None
    building: BuildingInput | None = None
    features: FeaturesInput | None = None
    amenities: list[str] | None = None
    tags: list[str] | None = None

    @field_validator("title")
    @classmethod
    def validate_title(cls, value: str | None) -> str | None:
        if value is not None:
            return strip_non_empty_title(value)
        return value

    @field_validator("tags")
    @classmethod
    def validate_tags(cls, value: list[str] | None) -> list[str] | None:
        if value is not None:
            return validate_tag_lengths(value)
        return value

    @field_validator("amenities")
    @classmethod
    def validate_amenities(cls, value: list[str] | None) -> list[str] | None:
        if value is None:
            return value
        unknown = sorted(set(value) - KNOWN_AMENITY_CODES)
        if unknown:
            raise ValueError(f"Unknown amenities: {', '.join(unknown)}")
        return value


class StatusChangeRequest(BaseModel):
    version: int = Field(..., ge=1)
    status: PropertyStatus
    reason: str | None = None


class ImageResponse(BaseModel):
    id: UUID
    url: str | None = None
    is_primary: bool = False
    sort_order: int = 0
    caption: str | None = None


class DocumentResponse(BaseModel):
    id: UUID
    document_type: DocumentType
    url: str | None = None
    verified: bool = False


class ListingResponse(BaseModel):
    provider: str | None = None
    listing_id: str | None = None
    original_url: str | None = None


class OwnershipResponse(BaseModel):
    id: UUID
    owner_name: str
    ownership_percentage: str
    is_current: bool = True


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
    parcel: ParcelResponse | None = None
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
    primary_image_url: str | None = None
    distance_meters: float | None = None
    created_at: datetime | None = None
