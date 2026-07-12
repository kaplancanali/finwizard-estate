from __future__ import annotations

from property_service.domain.enums._base import StrEnum


class SyncStatus(StrEnum):
    PENDING = "pending"
    SYNCED = "synced"
    FAILED = "failed"
    STALE = "stale"
