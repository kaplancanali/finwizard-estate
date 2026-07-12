from __future__ import annotations

from uuid import UUID

from property_service.application.dto.property_create_dto import CreatePropertyDTO
from property_service.application.dto.property_search_dto import (
    GeoCriteria,
    PropertySearchCriteria,
    SearchFilterSet,
    SortCriteria,
)
from property_service.presentation.schemas.property_schemas import PropertyCreateRequest
from property_service.presentation.schemas.search_schemas import PropertySearchRequest


def create_property_dto_from_request(
    request: PropertyCreateRequest,
    tenant_id: UUID,
    user_id: UUID,
) -> CreatePropertyDTO:
    pricing = request.pricing
    parcel = request.parcel
    location = request.location
    return CreatePropertyDTO(
        tenant_id=tenant_id,
        created_by=user_id,
        title=request.title,
        description=request.description,
        property_type=request.property_type,
        property_category=request.property_category,
        property_subtype=request.property_subtype,
        status=request.status,
        visibility=request.visibility,
        location_country_code=location.country_code,
        province=location.province,
        district=location.district,
        neighborhood=location.neighborhood,
        street=location.street,
        postal_code=location.postal_code,
        address_line=location.address_line,
        latitude=location.latitude,
        longitude=location.longitude,
        elevation=location.elevation,
        sale_price=pricing.sale_price if pricing else None,
        rental_price=pricing.rental_price if pricing else None,
        maintenance_fee=pricing.maintenance_fee if pricing else None,
        currency=pricing.currency if pricing else "TRY",
        price_on_request=pricing.price_on_request if pricing else False,
        parcel_block=parcel.block if parcel else None,
        parcel_number=parcel.parcel_number if parcel else None,
        parcel_area_sqm=parcel.parcel_area_sqm if parcel else None,
        cadastral_reference=parcel.cadastral_reference if parcel else None,
        zoning_type=parcel.zoning_type if parcel else None,
        building=request.building.model_dump() if request.building else None,
        features=request.features.model_dump() if request.features else None,
        amenities=request.amenities,
        tags=request.tags,
        source_type=request.source.source_type,
        source_reference=request.source.source_reference,
        source_payload=request.source.source_payload,
    )


def search_criteria_from_request(
    request: PropertySearchRequest,
    tenant_id: UUID | None = None,
) -> PropertySearchCriteria:
    return PropertySearchCriteria(
        tenant_id=tenant_id,
        query=request.query,
        filters=SearchFilterSet(raw=request.filters_dict()),
        geo=GeoCriteria(type=request.geo.type, payload=request.geo_dict()) if request.geo else None,
        sort=[SortCriteria(field=item.field, direction=item.direction) for item in request.sort],
        page=request.page,
        page_size=request.page_size,
        include_facets=request.include_facets,
    )
