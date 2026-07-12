from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime
from decimal import Decimal
from uuid import UUID, uuid4

from property_service.domain.enums.owner_type import OwnerType


@dataclass
class PropertyOwnership:
    owner_type: OwnerType
    owner_name: str
    ownership_percentage: Decimal
    owner_external_id: UUID | None = None
    acquired_at: date | None = None
    released_at: date | None = None
    is_current: bool = True
    id: UUID = field(default_factory=uuid4)


@dataclass
class OwnershipHistoryEntry:
    """Append-only ownership snapshot (property_ownership_history)."""

    owner_type: OwnerType
    owner_name: str
    ownership_percentage: Decimal
    owner_external_id: UUID | None = None
    acquired_at: date | None = None
    released_at: date | None = None
    effective_from: datetime | None = None
    effective_to: datetime | None = None
    id: UUID = field(default_factory=uuid4)
