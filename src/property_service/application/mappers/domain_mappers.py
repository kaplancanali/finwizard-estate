from __future__ import annotations

from uuid import UUID

from property_service.application.dto.property_create_dto import CreatePropertyDTO
from property_service.domain.entities.property_building import PropertyBuilding
from property_service.domain.entities.property_features import PropertyFeatures
from property_service.domain.entities.property_image import PropertyAmenity
from property_service.domain.entities.property_location import PropertyLocation
from property_service.domain.entities.property_parcel import PropertyParcel
from property_service.domain.entities.property_pricing import PropertyPricing
from property_service.domain.entities.property_version import PropertyExternalSource
from property_service.domain.enums.source_type import SourceType
from property_service.domain.factories.property_factory import CreatePropertyData
from property_service.domain.value_objects.geo_coordinate import GeoCoordinate


def create_property_data_from_dto(dto: CreatePropertyDTO) -> CreatePropertyData:
    coordinate = None
    if dto.latitude is not None and dto.longitude is not None:
        coordinate = GeoCoordinate(dto.latitude, dto.longitude)

    location = PropertyLocation(
        country_code=dto.location_country_code,
        province=dto.province,
        district=dto.district,
        neighborhood=dto.neighborhood,
        street=dto.street,
        postal_code=dto.postal_code,
        address_line=dto.address_line,
        coordinate=coordinate,
    )

    pricing = PropertyPricing(
        sale_price=dto.sale_price,
        rental_price=dto.rental_price,
        maintenance_fee=dto.maintenance_fee,
        currency=dto.currency,
        price_on_request=dto.price_on_request,
    )

    parcel = None
    if any([dto.parcel_block, dto.parcel_number, dto.cadastral_reference]):
        parcel = PropertyParcel(
            block=dto.parcel_block,
            parcel_number=dto.parcel_number,
            parcel_area_sqm=dto.parcel_area_sqm,
            cadastral_reference=dto.cadastral_reference,
            zoning_type=dto.zoning_type,
        )

    building = PropertyBuilding(**dto.building) if dto.building else None
    features = PropertyFeatures(**dto.features) if dto.features else None
    amenities = [PropertyAmenity(amenity_code=code) for code in dto.amenities]

    return CreatePropertyData(
        tenant_id=dto.tenant_id,
        created_by=dto.created_by,
        title=dto.title,
        description=dto.description,
        property_type=dto.property_type,
        property_category=dto.property_category,
        property_subtype=dto.property_subtype,
        status=dto.status,
        visibility=dto.visibility,
        location=location,
        pricing=pricing,
        building=building,
        parcel=parcel,
        features=features,
        amenities=amenities,
        tags=dto.tags,
        source_type=dto.source_type,
        source_reference=dto.source_reference,
        source_payload=dto.source_payload,
    )


def external_source_from_dto(dto: CreatePropertyDTO) -> PropertyExternalSource:
    return PropertyExternalSource(
        source_type=dto.source_type or SourceType.MANUAL,
        external_id=dto.source_reference,
    )
