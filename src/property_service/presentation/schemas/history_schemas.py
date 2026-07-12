from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel


class PriceHistoryResponse(BaseModel):
    id: UUID
    price_type: str
    old_amount: Decimal | None
    new_amount: Decimal | None
    currency: str | None
    changed_at: datetime | None = None
    changed_by: UUID | None = None
    change_reason: str | None = None


class StatusHistoryResponse(BaseModel):
    id: UUID
    old_status: str
    new_status: str
    changed_at: datetime | None = None
    changed_by: UUID | None = None
    reason: str | None = None


class OwnershipHistoryResponse(BaseModel):
    id: UUID
    owner_type: str
    owner_name: str
    ownership_percentage: Decimal
    acquired_at: date | None = None
    released_at: date | None = None
    effective_from: datetime | None = None
    effective_to: datetime | None = None


class VersionSummaryResponse(BaseModel):
    id: UUID
    version_number: int
    change_summary: str | None
    created_at: datetime | None = None
    created_by: UUID | None = None


class AuditLogResponse(BaseModel):
    id: UUID
    action: str
    actor_id: UUID
    actor_type: str
    changes: dict[str, object] | None = None
    correlation_id: UUID | None = None
    created_at: datetime | None = None
