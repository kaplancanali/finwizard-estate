from __future__ import annotations

import json
from typing import Any

from property_service.domain.events.base import DomainEvent
from property_service.infrastructure.messaging.cloudevents import build_cloudevent


class EventSerializer:
    def to_cloudevent(self, event: DomainEvent, *, correlation_id: str | None = None) -> dict[str, Any]:
        return build_cloudevent(event, correlation_id=correlation_id)

    def serialize(self, event: DomainEvent, *, correlation_id: str | None = None) -> dict[str, Any]:
        envelope = self.to_cloudevent(event, correlation_id=correlation_id)
        envelope["routing_key"] = event.routing_key
        envelope["event_version"] = event.event_version
        return envelope

    def to_json(self, event: DomainEvent, *, correlation_id: str | None = None) -> str:
        return json.dumps(self.serialize(event, correlation_id=correlation_id), default=str)
