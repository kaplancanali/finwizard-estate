from __future__ import annotations

from property_service.application.mappers.domain_mappers import create_property_data_from_dto
from property_service.application.dto.property_create_dto import CreatePropertyDTO
from property_service.domain.entities.property_building import PropertyBuilding
from property_service.domain.entities.property_features import PropertyFeatures
from property_service.domain.entities.property_location import PropertyLocation
from property_service.domain.entities.property_pricing import PropertyPricing
from property_service.domain.factories.property_factory import CreatePropertyData
from property_service.domain.value_objects.geo_coordinate import GeoCoordinate
from property_service.presentation.mappers.request_mappers import (
    create_property_dto_from_request,
    search_criteria_from_request,
)
from property_service.presentation.mappers.response_mappers import (
    property_to_detail,
    property_to_response,
    summary_to_response,
)
from property_service.presentation.schemas.property_schemas import (
    BuildingSchema,
    FeaturesSchema,
    LocationSchema,
    PricingSchema,
    PropertyCreateRequest,
)


def location_from_schema(schema: LocationSchema) -> PropertyLocation:
    coordinate = None
    if schema.latitude is not None and schema.longitude is not None:
        coordinate = GeoCoordinate(schema.latitude, schema.longitude)
    return PropertyLocation(
        country_code=schema.country_code,
        province=schema.province,
        district=schema.district,
        neighborhood=schema.neighborhood,
        street=schema.street,
        postal_code=schema.postal_code,
        address_line=schema.address_line,
        coordinate=coordinate,
        elevation=schema.elevation,
    )


def pricing_from_schema(schema: PricingSchema | None) -> PropertyPricing | None:
    if schema is None:
        return None
    return PropertyPricing(
        sale_price=schema.sale_price,
        rental_price=schema.rental_price,
        maintenance_fee=schema.maintenance_fee,
        currency=schema.currency,
        price_on_request=schema.price_on_request,
    )


def building_from_schema(schema: BuildingSchema | None) -> PropertyBuilding | None:
    if schema is None:
        return None
    return PropertyBuilding(**schema.model_dump())


def features_from_schema(schema: FeaturesSchema | None) -> PropertyFeatures | None:
    if schema is None:
        return None
    return PropertyFeatures(**schema.model_dump())


def create_dto_from_request(
    request: PropertyCreateRequest,
    tenant_id,
    user_id,
) -> CreatePropertyData:
    dto = create_property_dto_from_request(request, tenant_id, user_id)
    return create_property_data_from_dto(dto)


__all__ = [
    "CreatePropertyDTO",
    "building_from_schema",
    "create_dto_from_request",
    "create_property_data_from_dto",
    "create_property_dto_from_request",
    "features_from_schema",
    "location_from_schema",
    "pricing_from_schema",
    "property_to_detail",
    "property_to_response",
    "search_criteria_from_request",
    "summary_to_response",
]
