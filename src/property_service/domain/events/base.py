from __future__ import annotations

import re
from abc import ABC
from dataclasses import dataclass, field
from datetime import datetime, timezone
from decimal import Decimal
from enum import Enum
from uuid import UUID, uuid4

from property_service.domain.events.catalog import EVENT_CATALOG, EVENT_SOURCE


@dataclass
class DomainEvent(ABC):
    event_id: UUID = field(default_factory=uuid4)
    occurred_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    aggregate_id: UUID | None = None
    tenant_id: UUID | None = None
    correlation_id: UUID | None = None
    actor_id: UUID | None = None

    @property
    def event_name(self) -> str:
        name = self.__class__.__name__
        s1 = re.sub(r"(.)([A-Z][a-z]+)", r"\1.\2", name)
        return re.sub(r"([a-z0-9])([A-Z])", r"\1.\2", s1).lower()

    @property
    def event_type(self) -> str:
        """CloudEvents type stored in outbox.event_type."""
        return self.cloud_events_type

    @property
    def event_version(self) -> int:
        definition = EVENT_CATALOG.get(self.__class__.__name__)
        return definition.version if definition else 1

    @property
    def routing_key(self) -> str:
        definition = EVENT_CATALOG.get(self.__class__.__name__)
        if definition:
            return definition.routing_key
        return f"{self.event_name}.v{self.event_version}"

    @property
    def cloud_events_type(self) -> str:
        definition = EVENT_CATALOG.get(self.__class__.__name__)
        if definition:
            return definition.cloud_events_type
        return f"com.finward.{self.event_name}.v{self.event_version}"

    @property
    def event_source(self) -> str:
        return EVENT_SOURCE

    def to_payload(self) -> dict[str, object]:
        payload: dict[str, object] = {}
        for key, value in self.__dict__.items():
            if key in ("event_id", "occurred_at", "aggregate_id", "tenant_id", "correlation_id", "actor_id"):
                continue
            payload[key] = _serialize(value)
        if self.tenant_id:
            payload.setdefault("tenant_id", str(self.tenant_id))
        return payload


def _serialize(value: object) -> object:
    if isinstance(value, UUID):
        return str(value)
    if isinstance(value, datetime):
        return value.isoformat()
    if isinstance(value, Decimal):
        return float(value)
    if isinstance(value, Enum):
        return value.value
    if isinstance(value, dict):
        return {k: _serialize(v) for k, v in value.items()}
    if isinstance(value, list):
        return [_serialize(v) for v in value]
    return value
