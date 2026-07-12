from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID, uuid4

from property_service.domain.enums.document_type import DocumentType


@dataclass
class PropertyDocument:
    document_type: DocumentType
    storage_key: str
    url: str | None = None
    file_name: str | None = None
    mime_type: str | None = None
    file_size: int | None = None
    verified: bool = False
    verified_at: datetime | None = None
    verified_by: UUID | None = None
    id: UUID = field(default_factory=uuid4)
    deleted_at: datetime | None = None
