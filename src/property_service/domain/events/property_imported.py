from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID

from property_service.domain.events.base import DomainEvent


@dataclass
class PropertyImported(DomainEvent):
    job_id: UUID | None = None
    source_type: str = ""
    total: int = 0
    created_count: int = 0
    skipped: int = 0
    failed: int = 0
    created_property_ids: list[UUID] | None = None
    failed_items: list[dict[str, object]] | None = None

    def __post_init__(self) -> None:
        if self.created_property_ids is None:
            self.created_property_ids = []
        if self.failed_items is None:
            self.failed_items = []

    def to_payload(self) -> dict[str, object]:
        return {
            "job_id": str(self.job_id) if self.job_id else None,
            "tenant_id": str(self.tenant_id) if self.tenant_id else None,
            "source_type": self.source_type,
            "summary": {
                "total": self.total,
                "created": self.created_count,
                "skipped": self.skipped,
                "failed": self.failed,
            },
            "created_property_ids": [str(i) for i in self.created_property_ids or []],
            "failed_items": self.failed_items or [],
            "completed_at": self.occurred_at.isoformat(),
        }
