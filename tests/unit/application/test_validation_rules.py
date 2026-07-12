from __future__ import annotations

from decimal import Decimal
from uuid import uuid4

import pytest
from pydantic import ValidationError as PydanticValidationError

from property_service.application.auth_context import AuthContext
from property_service.application.services.business_validator import BusinessValidator
from property_service.application.services.metadata_validator import MetadataSchemaValidator
from property_service.domain.entities.property_building import PropertyBuilding
from property_service.domain.entities.property_ownership import PropertyOwnership
from property_service.domain.enums.owner_type import OwnerType
from property_service.domain.enums.property_type import PropertyType
from property_service.domain.exceptions import AuthorizationError, ValidationError
from property_service.domain.services.listing_validator import ListingValidator
from property_service.domain.services.property_validator import PropertyValidator
from property_service.presentation.schemas.field_validators import validate_price_digits, validate_room_count_increment
from property_service.presentation.schemas.property_schemas import LocationInput, PropertyCreateRequest
from property_service.domain.enums.property_category import PropertyCategory


class TestInputValidation:
    def test_title_rejects_whitespace_only(self) -> None:
        with pytest.raises(PydanticValidationError):
            PropertyCreateRequest(
                title="   ",
                property_type=PropertyType.APARTMENT,
                property_category=PropertyCategory.RESIDENTIAL,
                location=LocationInput(country_code="TR", province="Istanbul"),
            )

    def test_unknown_amenity_rejected(self) -> None:
        with pytest.raises(PydanticValidationError):
            PropertyCreateRequest(
                title="Valid Title",
                property_type=PropertyType.APARTMENT,
                property_category=PropertyCategory.RESIDENTIAL,
                location=LocationInput(country_code="TR", province="Istanbul"),
                amenities=["jacuzzi"],
            )

    def test_room_count_half_step(self) -> None:
        assert validate_room_count_increment(Decimal("2.5")) == Decimal("2.5")
        with pytest.raises(ValueError):
            validate_room_count_increment(Decimal("2.3"))

    def test_price_digit_limit(self) -> None:
        with pytest.raises(ValueError):
            validate_price_digits(Decimal("1" * 16))


class TestDomainValidationRules:
    def test_duplicate_owner_rejected(self) -> None:
        existing = [
            PropertyOwnership(
                owner_type=OwnerType.INDIVIDUAL,
                owner_name="Alice",
                ownership_percentage=Decimal("50"),
                is_current=True,
            )
        ]
        duplicate = PropertyOwnership(
            owner_type=OwnerType.INDIVIDUAL,
            owner_name="Alice",
            ownership_percentage=Decimal("10"),
            is_current=True,
        )
        with pytest.raises(ValidationError) as exc_info:
            PropertyValidator.validate_ownership(existing, duplicate)
        assert exc_info.value.code == "DUPLICATE_OWNER"

    def test_listing_url_invalid(self) -> None:
        with pytest.raises(ValidationError) as exc_info:
            ListingValidator.validate_url("not-a-url")
        assert exc_info.value.code == "INVALID_LISTING_URL"

    def test_metadata_schema_rejects_extra_fields_for_apartment(self) -> None:
        validator = MetadataSchemaValidator()
        with pytest.raises(ValidationError):
            validator.validate("apartment", {"custom_field": "ok", "unexpected": True})


class TestBusinessValidation:
    def test_missing_permission_forbidden(self) -> None:
        auth = AuthContext(user_id=uuid4(), tenant_id=uuid4(), permissions=frozenset())
        with pytest.raises(AuthorizationError):
            BusinessValidator.require_permission(auth, "property:create")

    def test_bulk_limit_exceeded(self) -> None:
        from property_service.domain.exceptions import BulkLimitExceededError

        with pytest.raises(BulkLimitExceededError) as exc_info:
            BusinessValidator.assert_bulk_limit(1001)
        assert exc_info.value.code == "BULK_LIMIT_EXCEEDED"
