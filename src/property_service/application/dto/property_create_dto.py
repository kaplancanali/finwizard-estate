from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal
from typing import Any
from uuid import UUID

from property_service.domain.enums.property_category import PropertyCategory
from property_service.domain.enums.property_status import PropertyStatus
from property_service.domain.enums.property_type import PropertyType
from property_service.domain.enums.property_visibility import PropertyVisibility
from property_service.domain.enums.source_type import SourceType


@dataclass
class CreatePropertyDTO:
    tenant_id: UUID
    created_by: UUID
    title: str
    property_type: PropertyType
    property_category: PropertyCategory
    location_country_code: str
    source_type: SourceType = SourceType.MANUAL
    description: str | None = None
    property_subtype: str | None = None
    status: PropertyStatus = PropertyStatus.DRAFT
    visibility: PropertyVisibility = PropertyVisibility.PRIVATE
    source_reference: str | None = None
    source_payload: dict | None = None
    province: str | None = None
    district: str | None = None
    neighborhood: str | None = None
    street: str | None = None
    postal_code: str | None = None
    address_line: str | None = None
    latitude: Decimal | None = None
    longitude: Decimal | None = None
    elevation: Decimal | None = None
    sale_price: Decimal | None = None
    rental_price: Decimal | None = None
    maintenance_fee: Decimal | None = None
    currency: str | None = "TRY"
    price_on_request: bool = False
    parcel_block: str | None = None
    parcel_number: str | None = None
    parcel_area_sqm: Decimal | None = None
    cadastral_reference: str | None = None
    zoning_type: str | None = None
    building: dict | None = None
    features: dict | None = None
    amenities: list[str] = field(default_factory=list)
    tags: list[str] = field(default_factory=list)

    @classmethod
    def from_bulk_payload(cls, raw: dict[str, Any], *, tenant_id: UUID, user_id: UUID) -> CreatePropertyDTO:
        location = raw.get("location") or {}
        pricing = raw.get("pricing")
        parcel = raw.get("parcel")
        source = raw.get("source") or {}
        return cls(
            tenant_id=tenant_id,
            created_by=user_id,
            title=str(raw["title"]),
            description=raw.get("description"),
            property_type=PropertyType(raw["property_type"]),
            property_category=PropertyCategory(raw["property_category"]),
            property_subtype=raw.get("property_subtype"),
            status=PropertyStatus(raw.get("status", PropertyStatus.DRAFT.value)),
            visibility=PropertyVisibility(raw.get("visibility", PropertyVisibility.PRIVATE.value)),
            location_country_code=str(location.get("country_code", "TR")),
            province=location.get("province"),
            district=location.get("district"),
            neighborhood=location.get("neighborhood"),
            street=location.get("street"),
            postal_code=location.get("postal_code"),
            address_line=location.get("address_line"),
            latitude=_decimal_or_none(location.get("latitude")),
            longitude=_decimal_or_none(location.get("longitude")),
            elevation=_decimal_or_none(location.get("elevation")),
            sale_price=_decimal_or_none(pricing.get("sale_price")) if pricing else None,
            rental_price=_decimal_or_none(pricing.get("rental_price")) if pricing else None,
            maintenance_fee=_decimal_or_none(pricing.get("maintenance_fee")) if pricing else None,
            currency=pricing.get("currency", "TRY") if pricing else "TRY",
            price_on_request=bool(pricing.get("price_on_request", False)) if pricing else False,
            parcel_block=parcel.get("block") if parcel else None,
            parcel_number=parcel.get("parcel_number") if parcel else None,
            parcel_area_sqm=_decimal_or_none(parcel.get("parcel_area_sqm")) if parcel else None,
            cadastral_reference=parcel.get("cadastral_reference") if parcel else None,
            zoning_type=parcel.get("zoning_type") if parcel else None,
            building=raw.get("building"),
            features=raw.get("features"),
            amenities=list(raw.get("amenities") or []),
            tags=list(raw.get("tags") or []),
            source_type=SourceType(source.get("source_type", SourceType.MANUAL.value)),
            source_reference=source.get("source_reference"),
            source_payload=source.get("source_payload"),
        )


def _decimal_or_none(value: object) -> Decimal | None:
    if value is None:
        return None
    return Decimal(str(value))


PropertyCreateDTO = CreatePropertyDTO
