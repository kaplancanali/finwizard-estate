from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID, uuid4

from property_service.domain.enums.source_type import SourceType


@dataclass
class PropertyExternalSource:
    source_type: SourceType
    source_reference: str | None = None
    source_payload: dict[str, object] | None = None
    imported_at: datetime | None = None
    id: UUID = field(default_factory=uuid4)


@dataclass
class PropertyMetadata:
    metadata: dict[str, object] = field(default_factory=dict)
    tenant_extensions: dict[str, object] = field(default_factory=dict)
    schema_version: str = "1.0"


@dataclass
class PropertyVersion:
    version_number: int
    snapshot: dict[str, object]
    change_summary: str | None = None
    created_by: UUID | None = None
    id: UUID = field(default_factory=uuid4)


@dataclass
class PropertyAuditLog:
    action: str
    actor_id: UUID
    actor_type: str = "user"
    changes: dict[str, object] | None = None
    ip_address: str | None = None
    correlation_id: UUID | None = None
    id: UUID = field(default_factory=uuid4)


@dataclass
class StatusHistoryEntry:
    old_status: str
    new_status: str
    changed_by: UUID | None = None
    reason: str | None = None
    id: UUID = field(default_factory=uuid4)
