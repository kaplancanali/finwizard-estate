from __future__ import annotations

from decimal import Decimal
from uuid import uuid4

from property_service.domain.events import PropertyCreated
from property_service.infrastructure.celery.beat_schedule import beat_schedule
from property_service.infrastructure.messaging.cloudevents import (
    build_cloudevent,
    build_cloudevent_from_outbox,
)
from property_service.infrastructure.messaging.event_serializer import EventSerializer


def _sample_event() -> PropertyCreated:
    property_id = uuid4()
    tenant_id = uuid4()
    event = PropertyCreated(
        property_id=property_id,
        property_code="FW-TR-IST-00001234",
        slug="modern-apartment",
        property_type="apartment",
        property_category="residential",
        status="draft",
        source_type="manual",
        country_code="TR",
        sale_price=Decimal("8500000"),
        currency="TRY",
        created_by=uuid4(),
    )
    event.aggregate_id = property_id
    event.tenant_id = tenant_id
    event.correlation_id = uuid4()
    return event


class TestCloudEvents:
    def test_build_cloudevent_envelope(self) -> None:
        event = _sample_event()
        envelope = build_cloudevent(event)

        assert envelope["specversion"] == "1.0"
        assert envelope["id"] == str(event.event_id)
        assert envelope["source"] == "property-service"
        assert envelope["type"] == "com.finward.property.created.v1"
        assert envelope["datacontenttype"] == "application/json"
        assert envelope["subject"] == f"property/{event.property_id}"
        assert envelope["correlationid"] == str(event.correlation_id)
        assert envelope["tenantid"] == str(event.tenant_id)
        assert envelope["data"]["property_code"] == "FW-TR-IST-00001234"

    def test_build_cloudevent_from_outbox(self) -> None:
        event_id = uuid4()
        aggregate_id = uuid4()
        tenant_id = uuid4()
        envelope = build_cloudevent_from_outbox(
            event_id=event_id,
            event_type="com.finward.property.created.v1",
            payload={"property_id": str(aggregate_id)},
            metadata={
                "correlation_id": "corr-1",
                "tenant_id": str(tenant_id),
                "occurred_at": "2026-06-30T12:00:00+00:00",
            },
            occurred_at="2026-06-30T12:00:00+00:00",
            aggregate_id=aggregate_id,
        )
        assert envelope["type"] == "com.finward.property.created.v1"
        assert envelope["correlationid"] == "corr-1"
        assert envelope["tenantid"] == str(tenant_id)

    def test_event_serializer_adds_routing_metadata(self) -> None:
        event = _sample_event()
        serialized = EventSerializer().serialize(event)
        assert serialized["routing_key"] == "property.created.v1"
        assert serialized["event_version"] == 1
        assert serialized["type"] == "com.finward.property.created.v1"


class TestBeatSchedule:
    def test_outbox_runs_every_five_seconds(self) -> None:
        entry = beat_schedule["publish-outbox"]
        assert entry["schedule"] == 5.0
        assert entry["task"] == "property.outbox.publish"
        assert entry["kwargs"]["batch_size"] == 100

    def test_maintenance_schedules_present(self) -> None:
        assert beat_schedule["refresh-statistics"]["task"] == "property.maintenance.refresh_statistics"
        assert beat_schedule["purge-outbox"]["task"] == "property.maintenance.purge_outbox"
        assert beat_schedule["cleanup-orphaned-images"]["task"] == "property.image.cleanup_orphaned"
        assert beat_schedule["sync-listings"]["task"] == "property.sync.listing"
