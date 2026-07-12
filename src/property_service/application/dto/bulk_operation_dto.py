from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID


@dataclass
class BulkOperationDTO:
    property_ids: list[UUID]
    operation: str
    payload: dict[str, object] | None = None
