from __future__ import annotations

from decimal import Decimal
from uuid import uuid4

import pytest

from property_service.domain.aggregates.property import Property
from property_service.domain.entities.property_building import PropertyBuilding
from property_service.domain.entities.property_location import PropertyLocation
from property_service.domain.entities.property_ownership import PropertyOwnership
from property_service.domain.entities.property_pricing import PropertyPricing
from property_service.domain.entities.property_version import PropertyExternalSource
from property_service.domain.enums.owner_type import OwnerType
from property_service.domain.enums.property_category import PropertyCategory
from property_service.domain.enums.property_status import PropertyStatus
from property_service.domain.enums.property_type import PropertyType
from property_service.domain.enums.source_type import SourceType
from property_service.domain.exceptions import ValidationError
from property_service.domain.services.property_validator import PropertyValidator
from property_service.domain.specifications.base import ActivePropertySpec, PriceRangeSpec, TenantPropertySpec
from property_service.domain.value_objects.geo_coordinate import GeoCoordinate
from property_service.domain.value_objects.property_classification import PropertyClassification
from property_service.domain.value_objects.property_code import PropertyCode
from property_service.domain.value_objects.slug import Slug


def _make_prop(**overrides):
    tenant_id = overrides.pop("tenant_id", uuid4())
    location = PropertyLocation(
        country_code="TR",
        province="İstanbul",
        coordinate=GeoCoordinate(Decimal("41.0"), Decimal("29.0")),
    )
    return Property.create(
        tenant_id=tenant_id,
        property_code=PropertyCode("FW-TR-IST-00000099"),
        slug=Slug("spec-test"),
        title="Spec Test",
        classification=PropertyClassification(PropertyType.APARTMENT, PropertyCategory.RESIDENTIAL),
        location=location,
        created_by=uuid4(),
        source=PropertyExternalSource(source_type=SourceType.MANUAL),
        **overrides,
    )


def assert_validation_error(callable_, code: str) -> None:
    with pytest.raises(ValidationError) as exc_info:
        callable_()
    assert exc_info.value.code == code


class TestPropertyValidator:
    def test_land_with_rooms_fails(self):
        building = PropertyBuilding(room_count=Decimal("3"), floor_number=2)

        def validate():
            PropertyValidator.validate_building(building, PropertyType.LAND)

        assert_validation_error(validate, "INVALID_FIELDS_FOR_TYPE")

    def test_net_exceeds_gross_fails(self):
        building = PropertyBuilding(net_area_sqm=Decimal("150"), gross_area_sqm=Decimal("100"))

        def validate():
            PropertyValidator.validate_building(building, PropertyType.APARTMENT)

        assert_validation_error(validate, "AREA_INVALID")

    def test_ownership_exceeds_100(self):
        existing = [
            PropertyOwnership(
                owner_type=OwnerType.INDIVIDUAL,
                owner_name="A",
                ownership_percentage=Decimal("60"),
            )
        ]
        new = PropertyOwnership(
            owner_type=OwnerType.INDIVIDUAL,
            owner_name="B",
            ownership_percentage=Decimal("50"),
        )

        def validate():
            PropertyValidator.validate_ownership(existing, new)

        assert_validation_error(validate, "OWNERSHIP_EXCEEDS_100")

    def test_duplicate_owner_fails(self):
        existing = [
            PropertyOwnership(
                owner_type=OwnerType.INDIVIDUAL,
                owner_name="Alice",
                ownership_percentage=Decimal("40"),
                is_current=True,
            )
        ]
        new = PropertyOwnership(
            owner_type=OwnerType.INDIVIDUAL,
            owner_name="Alice",
            ownership_percentage=Decimal("10"),
            is_current=True,
        )

        def validate():
            PropertyValidator.validate_ownership(existing, new)

        assert_validation_error(validate, "DUPLICATE_OWNER")


class TestSpecifications:
    def test_active_property_spec(self):
        prop = _make_prop()
        spec = ActivePropertySpec()
        assert spec.is_satisfied_by(prop) is False

        prop.change_status(PropertyStatus.ACTIVE, uuid4())
        assert spec.is_satisfied_by(prop) is True

    def test_tenant_spec(self):
        tenant_id = uuid4()
        prop = _make_prop(tenant_id=tenant_id)
        spec = TenantPropertySpec(tenant_id)
        assert spec.is_satisfied_by(prop) is True
        assert spec.is_satisfied_by(_make_prop()) is False

    def test_price_range_spec(self):
        prop = _make_prop(pricing=PropertyPricing(sale_price=Decimal("5000000"), currency="TRY"))
        assert PriceRangeSpec(min_price=4000000, max_price=6000000).is_satisfied_by(prop) is True
        assert PriceRangeSpec(min_price=6000000).is_satisfied_by(prop) is False
