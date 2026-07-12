from __future__ import annotations

from property_service.domain.aggregates.property import Property
from property_service.presentation.schemas.property_schemas import (
    BuildingResponse,
    DocumentResponse,
    FeaturesResponse,
    ImageResponse,
    ListingResponse,
    LocationResponse,
    OwnershipResponse,
    ParcelResponse,
    PricingResponse,
    PropertyResponse,
    PropertySummaryResponse,
)
from property_service.application.dto.property_search_dto import PropertySummary


def property_to_response(prop: Property, *, include_related: bool = False) -> PropertyResponse:
    response = PropertyResponse(
        id=prop.id,
        tenant_id=prop.tenant_id,
        property_code=str(prop.property_code),
        slug=str(prop.slug),
        title=prop.title,
        description=prop.description,
        property_type=prop.classification.property_type,
        property_category=prop.classification.category,
        property_subtype=prop.classification.subtype,
        status=prop.status,
        visibility=prop.visibility,
        pricing=PricingResponse(
            sale_price=prop.pricing.sale_price,
            rental_price=prop.pricing.rental_price,
            maintenance_fee=prop.pricing.maintenance_fee,
            currency=prop.pricing.currency or "TRY",
            price_on_request=prop.pricing.price_on_request,
        ),
        location=LocationResponse(
            country_code=prop.location.country_code,
            province=prop.location.province,
            district=prop.location.district,
            neighborhood=prop.location.neighborhood,
            street=prop.location.street,
            postal_code=prop.location.postal_code,
            address_line=prop.location.address_line,
            latitude=prop.location.latitude,
            longitude=prop.location.longitude,
            elevation=prop.location.elevation,
        ),
        parcel=ParcelResponse(
            block=prop.parcel.block,
            parcel_number=prop.parcel.parcel_number,
            parcel_area_sqm=prop.parcel.parcel_area_sqm,
            cadastral_reference=prop.parcel.cadastral_reference,
            zoning_type=prop.parcel.zoning_type,
        )
        if prop.parcel and prop.parcel.has_parcel_info()
        else None,
        building=BuildingResponse(**prop.building.__dict__) if prop.building else None,
        features=FeaturesResponse(**prop.features.__dict__) if prop.features else None,
        amenities=[a.amenity_code for a in prop.amenities],
        tags=prop.tags,
        metadata=prop.metadata.metadata if prop.metadata else None,
        version=prop.version,
        published_at=prop.published_at,
        created_at=prop.created_at,
        updated_at=prop.updated_at,
        created_by=prop.created_by,
        updated_by=prop.updated_by,
    )

    if include_related:
        response.images = [
            ImageResponse(
                id=i.id,
                url=i.url,
                is_primary=i.is_primary,
                sort_order=i.sort_order,
                caption=i.caption,
            )
            for i in prop.active_images
        ]
        response.documents = [
            DocumentResponse(
                id=d.id,
                document_type=d.document_type,
                url=d.url,
                verified=d.verified,
            )
            for d in prop.active_documents
        ]
        response.ownership = [
            OwnershipResponse(
                id=o.id,
                owner_name=o.owner_name,
                ownership_percentage=str(o.ownership_percentage),
                is_current=o.is_current,
            )
            for o in prop.ownership
        ]
        if prop.listing:
            response.listing = ListingResponse(
                provider=prop.listing.provider.value if prop.listing.provider else None,
                listing_id=prop.listing.listing_id,
                original_url=prop.listing.original_url,
            )
    return response


def property_to_detail(prop: Property, include: str | None = None) -> dict:
    includes = {part.strip().lower() for part in include.split(",")} if include else set()
    include_related = bool(
        includes.intersection({"images", "documents", "ownership", "listing"})
    )
    base = property_to_response(prop, include_related=include_related).model_dump()
    if "history" in includes:
        base["price_history_count"] = len(prop.price_history)
        base["status_history_count"] = len(prop.status_history)
    return base


def summary_to_response(item: PropertySummary) -> PropertySummaryResponse:
    from property_service.domain.enums.property_status import PropertyStatus
    from property_service.domain.enums.property_type import PropertyType

    property_type = item.property_type
    if isinstance(property_type, str):
        property_type = PropertyType(property_type)
    status = item.status
    if isinstance(status, str):
        status = PropertyStatus(status)

    return PropertySummaryResponse(
        id=item.id,
        property_code=item.property_code,
        slug=item.slug,
        title=item.title,
        property_type=property_type,
        status=status,
        sale_price=item.sale_price,
        rental_price=item.rental_price,
        currency=item.currency,
        province=item.province,
        district=item.district,
        neighborhood=item.neighborhood,
        latitude=item.latitude,
        longitude=item.longitude,
        net_area_sqm=item.net_area_sqm,
        room_count=item.room_count,
        bathroom_count=item.bathroom_count,
        primary_image_url=item.primary_image_url,
        distance_meters=item.distance_meters,
        created_at=item.created_at,
    )
