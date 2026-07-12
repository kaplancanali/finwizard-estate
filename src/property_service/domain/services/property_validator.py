from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from property_service.domain.entities.property_building import PropertyBuilding
from property_service.domain.entities.property_image import PropertyImage
from property_service.domain.entities.property_location import PropertyLocation
from property_service.domain.entities.property_ownership import PropertyOwnership
from property_service.domain.entities.property_parcel import PropertyParcel
from property_service.domain.entities.property_pricing import PropertyPricing
from property_service.domain.enums.property_status import PropertyStatus
from property_service.domain.enums.property_type import PROPERTY_TYPE_CATEGORY_MAP, PropertyType
from property_service.domain.exceptions import ValidationError
from property_service.domain.value_objects.property_classification import PropertyClassification


class PropertyValidator:
    """Cross-field domain validation rules."""

    @staticmethod
    def validate_creation(
        *,
        classification: PropertyClassification,
        location: PropertyLocation,
        pricing: PropertyPricing | None,
        building: PropertyBuilding | None,
        parcel: PropertyParcel | None,
    ) -> None:
        PropertyValidator.validate_location(location)
        PropertyValidator.validate_type_category(classification)
        if pricing:
            PropertyValidator.validate_pricing(pricing, PropertyStatus.DRAFT)
        if building:
            PropertyValidator.validate_building(building, classification.property_type)
        if parcel and building and classification.property_type == PropertyType.LAND:
            if building.has_residential_fields():
                raise ValidationError(
                    "Land properties cannot have building residential fields",
                    code="INVALID_FIELDS_FOR_TYPE",
                )

    @staticmethod
    def validate_location(location: PropertyLocation) -> None:
        if not location.has_location():
            raise ValidationError(
                "Either coordinates or address components are required",
                code="LOCATION_REQUIRED",
            )

    @staticmethod
    def validate_type_category(classification: PropertyClassification) -> None:
        expected = PROPERTY_TYPE_CATEGORY_MAP.get(classification.property_type)
        if expected and classification.category.value != expected:
            # Allow explicit override for mixed/other types but warn via strict check for common mismatches
            if classification.property_type not in (PropertyType.OTHER, PropertyType.MIXED_PROJECT):
                raise ValidationError(
                    f"Property type '{classification.property_type.value}' "
                    f"does not match category '{classification.category.value}'",
                    code="TYPE_CATEGORY_MISMATCH",
                )

    @staticmethod
    def validate_pricing(pricing: PropertyPricing, status: PropertyStatus) -> None:
        if pricing.has_any_price() and not pricing.currency:
            raise ValidationError(
                "Currency is required when a price is set",
                code="CURRENCY_REQUIRED",
                field="pricing.currency",
            )
        if status == PropertyStatus.LISTED and not pricing.price_on_request:
            if not pricing.sale_price and not pricing.rental_price:
                raise ValidationError(
                    "Listed properties require a price or price_on_request flag",
                    code="PRICE_REQUIRED_FOR_LISTING",
                    field="pricing",
                )

    @staticmethod
    def validate_single_primary(images: list[PropertyImage]) -> None:
        primary_count = sum(
            1 for image in images if image.deleted_at is None and image.is_primary
        )
        if primary_count > 1:
            raise ValidationError(
                "Only one primary image is allowed",
                code="MULTIPLE_PRIMARY_IMAGES",
                field="images",
            )

    @staticmethod
    def validate_building(building: PropertyBuilding, property_type: PropertyType) -> None:
        if property_type == PropertyType.LAND and building.has_residential_fields():
            raise ValidationError(
                "Land properties cannot have residential building fields",
                code="INVALID_FIELDS_FOR_TYPE",
            )
        if (
            building.net_area_sqm is not None
            and building.gross_area_sqm is not None
            and building.net_area_sqm > building.gross_area_sqm
        ):
            raise ValidationError(
                "Net area cannot exceed gross area",
                code="AREA_INVALID",
                field="building.net_area_sqm",
            )
        if (
            building.floor_number is not None
            and building.floor_count is not None
            and building.floor_number > building.floor_count
        ):
            raise ValidationError(
                "Floor number cannot exceed floor count",
                code="FLOOR_INVALID",
                field="building.floor_number",
            )
        if building.construction_year is not None:
            current_year = datetime.now().year
            if building.construction_year > current_year + 5:
                raise ValidationError(
                    "Construction year cannot be more than 5 years in the future",
                    code="INVALID_CONSTRUCTION_YEAR",
                    field="building.construction_year",
                )
            if building.construction_year > current_year:
                raise ValidationError(
                    "Construction year cannot exceed the current year",
                    code="INVALID_CONSTRUCTION_YEAR",
                    field="building.construction_year",
                )

    @staticmethod
    def validate_status_transition(
        status: PropertyStatus,
        new_status: PropertyStatus,
        pricing: PropertyPricing,
        images: list[PropertyImage],
        location: PropertyLocation,
    ) -> None:
        if new_status == PropertyStatus.LISTED:
            if not pricing.price_on_request and not pricing.sale_price and not pricing.rental_price:
                raise ValidationError(
                    "Listed properties require a price or price_on_request flag",
                    code="PRICE_REQUIRED_FOR_LISTING",
                    field="pricing",
                )
            if not images:
                raise ValidationError(
                    "Listed properties require at least one image",
                    code="IMAGE_REQUIRED_FOR_LISTING",
                    field="images",
                )
        if new_status == PropertyStatus.ACTIVE:
            if location.coordinate is None:
                raise ValidationError(
                    "Active properties require coordinates",
                    code="COORDINATES_REQUIRED",
                    field="location",
                )

    @staticmethod
    def validate_ownership(
        existing: list[PropertyOwnership],
        new: PropertyOwnership,
    ) -> None:
        current = [o for o in existing if o.is_current]
        if new.is_current:
            current = current + [new]
        total = sum(o.ownership_percentage for o in current)
        if total > Decimal("100"):
            raise ValidationError(
                "Total ownership cannot exceed 100%",
                code="OWNERSHIP_EXCEEDS_100",
                field="ownership",
            )
        if new.is_current:
            for owner in existing:
                if (
                    owner.is_current
                    and owner.owner_type == new.owner_type
                    and owner.owner_name == new.owner_name
                ):
                    raise ValidationError(
                        "Duplicate current owner for the same owner type and name",
                        code="DUPLICATE_OWNER",
                        field="ownership",
                    )
        if (
            new.acquired_at is not None
            and new.released_at is not None
            and new.released_at < new.acquired_at
        ):
            raise ValidationError(
                "released_at must be on or after acquired_at",
                code="INVALID_OWNERSHIP_DATES",
                field="ownership.released_at",
            )
