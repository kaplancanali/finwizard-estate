from __future__ import annotations

from decimal import Decimal
from uuid import uuid4

import pytest

from property_service.domain.events import (
    EVENT_CATALOG,
    EVENT_EXCHANGE,
    EVENT_SOURCE,
    MAX_OUTBOX_RETRIES,
    OUTBOX_BATCH_SIZE,
    PropertyCreated,
    PropertyPriceChanged,
    PropertyStatusChanged,
)
from property_service.domain.events.catalog import CONSUMER_QUEUE_BINDINGS, DEAD_LETTER_EXCHANGE


class TestEventCatalog:
    def test_exchange_and_constants(self) -> None:
        assert EVENT_EXCHANGE == "property.events"
        assert DEAD_LETTER_EXCHANGE == "property.events.dlx"
        assert EVENT_SOURCE == "property-service"
        assert MAX_OUTBOX_RETRIES == 5
        assert OUTBOX_BATCH_SIZE == 100

    def test_all_catalog_entries_have_cloudevents_type(self) -> None:
        assert len(EVENT_CATALOG) == 13
        for name, definition in EVENT_CATALOG.items():
            assert definition.name == name
            assert definition.cloud_events_type == f"com.finward.{definition.routing_key}"
            assert definition.routing_key.startswith("property.")
            assert definition.routing_key.endswith(".v1")

    def test_consumer_queue_bindings(self) -> None:
        assert "valuation.property.events" in CONSUMER_QUEUE_BINDINGS
        assert "property.price_changed.v1" in CONSUMER_QUEUE_BINDINGS["valuation.property.events"]


class TestDomainEvents:
    def test_property_created_types(self) -> None:
        event = PropertyCreated(
            property_id=uuid4(),
            property_code="FW-TR-IST-00001234",
            slug="modern-apartment",
            property_type="apartment",
            property_category="residential",
            status="draft",
            source_type="manual",
            country_code="TR",
            sale_price=Decimal("8500000.00"),
            currency="TRY",
            created_by=uuid4(),
        )
        event.aggregate_id = event.property_id
        event.tenant_id = uuid4()

        assert event.event_type == "com.finward.property.created.v1"
        assert event.routing_key == "property.created.v1"
        assert event.event_version == 1
        assert event.event_source == "property-service"

        payload = event.to_payload()
        assert payload["property_code"] == "FW-TR-IST-00001234"
        assert payload["location"]["country_code"] == "TR"
        assert payload["pricing"]["sale_price"] == 8500000.0
        assert payload["pricing"]["currency"] == "TRY"

    def test_property_price_changed_payload(self) -> None:
        event = PropertyPriceChanged(
            property_id=uuid4(),
            price_type="sale",
            old_amount=Decimal("8000000"),
            new_amount=Decimal("8500000"),
            currency="TRY",
            changed_by=uuid4(),
        )
        payload = event.to_payload()
        assert payload["old_amount"] == 8000000.0
        assert payload["new_amount"] == 8500000.0

    def test_property_status_changed_payload(self) -> None:
        event = PropertyStatusChanged(
            property_id=uuid4(),
            old_status="draft",
            new_status="active",
            changed_by=uuid4(),
        )
        payload = event.to_payload()
        assert payload["old_status"] == "draft"
        assert payload["new_status"] == "active"
        assert event.cloud_events_type == "com.finward.property.status_changed.v1"
