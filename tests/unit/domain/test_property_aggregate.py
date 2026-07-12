from __future__ import annotations

from decimal import Decimal
from uuid import uuid4

import pytest

from property_service.domain.aggregates.property import Property
from property_service.domain.entities.property_building import PropertyBuilding
from property_service.domain.entities.property_image import PropertyImage
from property_service.domain.entities.property_location import PropertyLocation
from property_service.domain.entities.property_pricing import PropertyPricing
from property_service.domain.entities.property_version import PropertyExternalSource
from property_service.domain.enums.property_category import PropertyCategory
from property_service.domain.enums.property_status import PropertyStatus
from property_service.domain.enums.property_type import PropertyType
from property_service.domain.enums.source_type import SourceType
from property_service.domain.events import PropertyCreated, PropertyPriceChanged, PropertyStatusChanged
from property_service.domain.exceptions import (
    InvalidStatusTransitionError,
    PropertyDeletedError,
    ValidationError,
)
from property_service.domain.factories.property_factory import CreatePropertyData, PropertyFactory
from property_service.domain.services.property_code_generator import PropertyCodeGenerator
from property_service.domain.services.slug_generator import SlugGenerator
from property_service.domain.value_objects.geo_coordinate import GeoCoordinate
from property_service.domain.value_objects.property_classification import PropertyClassification
from property_service.domain.value_objects.property_code import PropertyCode
from property_service.domain.value_objects.slug import Slug


@pytest.fixture
def tenant_id():
    return uuid4()


@pytest.fixture
def user_id():
    return uuid4()


@pytest.fixture
def location():
    return PropertyLocation(
        country_code="TR",
        province="İstanbul",
        district="Kadıköy",
        neighborhood="Moda",
        coordinate=GeoCoordinate(Decimal("40.987600"), Decimal("29.023400")),
    )


@pytest.fixture
def classification():
    return PropertyClassification(
        property_type=PropertyType.APARTMENT,
        category=PropertyCategory.RESIDENTIAL,
    )


@pytest.fixture
def source():
    return PropertyExternalSource(source_type=SourceType.MANUAL)


def make_property(tenant_id, user_id, location, classification, source, **kwargs) -> Property:
    return Property.create(
        tenant_id=tenant_id,
        property_code=PropertyCode("FW-TR-IST-00000001"),
        slug=Slug("modern-apartment-kadikoy"),
        title="Modern Apartment in Kadıköy",
        classification=classification,
        location=location,
        created_by=user_id,
        source=source,
        pricing=kwargs.get("pricing"),
        building=kwargs.get("building"),
    )


def assert_validation_error(callable_, code: str) -> None:
    with pytest.raises(ValidationError) as exc_info:
        callable_()
    assert exc_info.value.code == code


class TestPropertyCreate:
    def test_creates_property_with_event(self, tenant_id, user_id, location, classification, source):
        prop = make_property(tenant_id, user_id, location, classification, source)
        events = prop.collect_events()

        assert prop.status == PropertyStatus.DRAFT
        assert prop.version == 1
        assert len(events) == 1
        assert isinstance(events[0], PropertyCreated)
        assert events[0].property_code == "FW-TR-IST-00000001"

    def test_requires_location(self, tenant_id, user_id, classification, source):
        empty_location = PropertyLocation(country_code="TR")

        def create():
            Property.create(
                tenant_id=tenant_id,
                property_code=PropertyCode("FW-TR-IST-00000002"),
                slug=Slug("test-property"),
                title="Test",
                classification=classification,
                location=empty_location,
                created_by=user_id,
                source=source,
            )

        assert_validation_error(create, "LOCATION_REQUIRED")

    def test_requires_currency_with_price(self, tenant_id, user_id, location, classification, source):
        def create():
            Property.create(
                tenant_id=tenant_id,
                property_code=PropertyCode("FW-TR-IST-00000003"),
                slug=Slug("priced-property"),
                title="Priced",
                classification=classification,
                location=location,
                created_by=user_id,
                source=source,
                pricing=PropertyPricing(sale_price=Decimal("1000000")),
            )

        assert_validation_error(create, "CURRENCY_REQUIRED")


class TestPropertyStatusTransitions:
    def test_draft_to_active(self, tenant_id, user_id, location, classification, source):
        prop = make_property(tenant_id, user_id, location, classification, source)
        prop.collect_events()
        prop.change_status(PropertyStatus.ACTIVE, user_id)
        assert prop.status == PropertyStatus.ACTIVE
        assert prop.published_at is not None

    def test_invalid_transition_raises(self, tenant_id, user_id, location, classification, source):
        prop = make_property(tenant_id, user_id, location, classification, source)
        with pytest.raises(InvalidStatusTransitionError):
            prop.change_status(PropertyStatus.LISTED, user_id)

    def test_listed_requires_price_and_image(self, tenant_id, user_id, location, classification, source):
        prop = make_property(tenant_id, user_id, location, classification, source)
        prop.change_status(PropertyStatus.ACTIVE, user_id)

        def to_listed_without_price():
            prop.change_status(PropertyStatus.LISTED, user_id)

        assert_validation_error(to_listed_without_price, "PRICE_REQUIRED_FOR_LISTING")

        prop.pricing = PropertyPricing(sale_price=Decimal("5000000"), currency="TRY")

        def to_listed_without_image():
            prop.change_status(PropertyStatus.LISTED, user_id)

        assert_validation_error(to_listed_without_image, "IMAGE_REQUIRED_FOR_LISTING")

    def test_full_listing_flow(self, tenant_id, user_id, location, classification, source):
        prop = make_property(
            tenant_id, user_id, location, classification, source,
            pricing=PropertyPricing(sale_price=Decimal("5000000"), currency="TRY"),
        )
        prop.change_status(PropertyStatus.ACTIVE, user_id)
        prop.add_image(PropertyImage(storage_key="img/1.jpg", url="https://example.com/1.jpg"), user_id)
        prop.collect_events()
        prop.change_status(PropertyStatus.LISTED, user_id, reason="Ready for market")
        events = prop.collect_events()
        assert any(isinstance(e, PropertyStatusChanged) for e in events)
        assert prop.status == PropertyStatus.LISTED


class TestPropertyPricing:
    def test_price_change_emits_event_and_history(self, tenant_id, user_id, location, classification, source):
        prop = make_property(
            tenant_id, user_id, location, classification, source,
            pricing=PropertyPricing(sale_price=Decimal("5000000"), currency="TRY"),
            building=PropertyBuilding(net_area_sqm=Decimal("100")),
        )
        prop.collect_events()

        new_pricing = PropertyPricing(sale_price=Decimal("4800000"), currency="TRY")
        prop.update_pricing(new_pricing, user_id, reason="Market adjustment")

        assert len(prop.price_history) == 1
        assert prop.price_history[0].old_amount == Decimal("5000000")
        assert prop.price_history[0].new_amount == Decimal("4800000")
        events = prop.collect_events()
        assert any(isinstance(e, PropertyPriceChanged) for e in events)
        assert prop.pricing.price_per_sqm == Decimal("48000.00")


class TestPropertySoftDelete:
    def test_soft_delete_and_restore(self, tenant_id, user_id, location, classification, source):
        prop = make_property(tenant_id, user_id, location, classification, source)
        prop.soft_delete(user_id)
        assert prop.is_deleted
        assert prop.status == PropertyStatus.DELETED

        with pytest.raises(PropertyDeletedError):
            prop.update_title("New Title", user_id)

        prop.restore(user_id)
        assert not prop.is_deleted
        assert prop.status == PropertyStatus.DRAFT


class TestPropertyFactory:
    def test_create_from_manual(self, tenant_id, user_id, location):
        factory = PropertyFactory()
        data = CreatePropertyData(
            tenant_id=tenant_id,
            created_by=user_id,
            title="Factory Property",
            property_type=PropertyType.VILLA,
            property_category=PropertyCategory.RESIDENTIAL,
            location=location,
            pricing=PropertyPricing(sale_price=Decimal("10000000"), currency="TRY"),
        )
        prop = factory.create_from_manual(data)
        assert prop.title == "Factory Property"
        assert prop.external_sources[0].source_type == SourceType.MANUAL
        assert str(prop.property_code).startswith("FW-TR-")


class TestValueObjects:
    def test_property_code_format(self):
        code = PropertyCode("FW-TR-IST-00001234")
        assert str(code) == "FW-TR-IST-00001234"

    def test_invalid_property_code(self):
        with pytest.raises(ValueError):
            PropertyCode("INVALID")

    def test_slug_from_title(self):
        slug = Slug.from_title("Modern Apartment in Kadıköy!")
        assert slug.value == "modern-apartment-in-kadkoy"

    def test_geo_coordinate_bounds(self):
        with pytest.raises(ValueError):
            GeoCoordinate(Decimal("91"), Decimal("0"))


class TestCodeAndSlugGenerators:
    def test_sequential_codes(self):
        gen = PropertyCodeGenerator()
        c1 = gen.generate("TR", "IST")
        c2 = gen.generate("TR", "IST")
        assert c1.value != c2.value

    def test_slug_collision(self):
        gen = SlugGenerator()
        s1 = gen.generate("Test Property", district="Moda")
        gen.register_existing(s1)
        s2 = gen.generate("Test Property", district="Moda")
        assert s2.value != s1.value
