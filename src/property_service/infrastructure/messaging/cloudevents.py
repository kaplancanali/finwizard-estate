from __future__ import annotations

from typing import Any
from uuid import UUID

from property_service.domain.events.base import DomainEvent
from property_service.domain.events.catalog import EVENT_SOURCE


def build_cloudevent(
    event: DomainEvent,
    *,
    correlation_id: str | None = None,
) -> dict[str, Any]:
    subject_id = event.aggregate_id or getattr(event, "property_id", None)
    return {
        "specversion": "1.0",
        "id": str(event.event_id),
        "source": EVENT_SOURCE,
        "type": event.cloud_events_type,
        "datacontenttype": "application/json",
        "time": event.occurred_at.isoformat(),
        "subject": f"property/{subject_id}" if subject_id else None,
        "correlationid": correlation_id or (str(event.correlation_id) if event.correlation_id else None),
        "tenantid": str(event.tenant_id) if event.tenant_id else None,
        "data": event.to_payload(),
    }


def build_cloudevent_from_outbox(
    *,
    event_id: UUID,
    event_type: str,
    payload: dict[str, object],
    metadata: dict[str, object] | None,
    occurred_at: str,
    aggregate_id: UUID,
) -> dict[str, Any]:
    meta = metadata or {}
    return {
        "specversion": "1.0",
        "id": str(event_id),
        "source": EVENT_SOURCE,
        "type": event_type,
        "datacontenttype": "application/json",
        "time": occurred_at,
        "subject": f"property/{aggregate_id}",
        "correlationid": meta.get("correlation_id"),
        "tenantid": meta.get("tenant_id"),
        "data": payload,
    }
