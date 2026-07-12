from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from uuid import UUID

from property_service.domain.aggregates.property import Property
from property_service.domain.entities.property_building import PropertyBuilding
from property_service.domain.entities.property_features import PropertyFeatures
from property_service.domain.entities.property_image import PropertyAmenity
from property_service.domain.entities.property_location import PropertyLocation
from property_service.domain.entities.property_parcel import PropertyParcel
from property_service.domain.entities.property_pricing import PropertyPricing
from property_service.domain.entities.property_version import PropertyExternalSource
from property_service.domain.enums.property_category import PropertyCategory
from property_service.domain.enums.property_status import PropertyStatus
from property_service.domain.enums.property_type import PropertyType
from property_service.domain.enums.property_visibility import PropertyVisibility
from property_service.domain.enums.source_type import SourceType
from property_service.domain.services.property_code_generator import PropertyCodeGenerator
from property_service.domain.services.slug_generator import SlugGenerator
from property_service.domain.value_objects.geo_coordinate import GeoCoordinate
from property_service.domain.value_objects.property_classification import PropertyClassification
from property_service.domain.value_objects.property_code import PropertyCode
from property_service.domain.value_objects.slug import Slug


@dataclass
class CreatePropertyData:
    tenant_id: UUID
    created_by: UUID
    title: str
    property_type: PropertyType
    property_category: PropertyCategory
    location: PropertyLocation
    description: str | None = None
    summary: str | None = None
    property_subtype: str | None = None
    pricing: PropertyPricing | None = None
    building: PropertyBuilding | None = None
    parcel: PropertyParcel | None = None
    features: PropertyFeatures | None = None
    amenities: list[PropertyAmenity] | None = None
    tags: list[str] | None = None
    status: PropertyStatus = PropertyStatus.DRAFT
    visibility: PropertyVisibility = PropertyVisibility.PRIVATE
    source_type: SourceType = SourceType.MANUAL
    source_reference: str | None = None
    source_payload: dict[str, object] | None = None


class PropertyFactory:
    def __init__(
        self,
        code_generator: PropertyCodeGenerator | None = None,
        slug_generator: SlugGenerator | None = None,
    ) -> None:
        self._code_generator = code_generator or PropertyCodeGenerator()
        self._slug_generator = slug_generator or SlugGenerator()

    def create_from_manual(self, data: CreatePropertyData) -> Property:
        return self._build(data, SourceType.MANUAL, data.source_reference)

    def create_from_address(self, data: CreatePropertyData) -> Property:
        return self._build(data, SourceType.ADDRESS, data.source_reference or data.location.address_line)

    def create_from_coordinates(self, data: CreatePropertyData) -> Property:
        if data.location.coordinate is None:
            raise ValueError("Coordinates required for create_from_coordinates")
        return self._build(
            data,
            SourceType.COORDINATES,
            f"{data.location.coordinate.latitude},{data.location.coordinate.longitude}",
        )

    def create_from_listing_url(self, data: CreatePropertyData, url: str) -> Property:
        data.source_reference = url
        return self._build(data, SourceType.LISTING_URL, url)

    def create_from_parcel(self, data: CreatePropertyData) -> Property:
        ref = None
        if data.parcel:
            ref = f"{data.parcel.block}/{data.parcel.parcel_number}"
        return self._build(data, SourceType.PARCEL, ref)

    def create_from_map_selection(self, data: CreatePropertyData, geojson_ref: str) -> Property:
        return self._build(data, SourceType.MAP_SELECTION, geojson_ref)

    def _build(
        self,
        data: CreatePropertyData,
        source_type: SourceType,
        source_reference: str | None,
    ) -> Property:
        region = data.location.district or data.location.province or "GEN"
        property_code = self._code_generator.generate(data.location.country_code, region)
        slug = self._slug_generator.generate(data.title, district=data.location.district)

        classification = PropertyClassification(
            property_type=data.property_type,
            category=data.property_category,
            subtype=data.property_subtype,
        )

        source = PropertyExternalSource(
            source_type=source_type,
            source_reference=source_reference,
            source_payload=data.source_payload,
        )

        return Property.create(
            tenant_id=data.tenant_id,
            property_code=property_code,
            slug=slug,
            title=data.title,
            classification=classification,
            location=data.location,
            created_by=data.created_by,
            source=source,
            description=data.description,
            summary=data.summary,
            pricing=data.pricing,
            building=data.building,
            parcel=data.parcel,
            features=data.features,
            amenities=data.amenities,
            tags=data.tags,
            status=data.status,
            visibility=data.visibility,
        )
