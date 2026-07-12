from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID, uuid4

from property_service.domain.enums.processing_status import ProcessingStatus


@dataclass
class PropertyAmenity:
    amenity_code: str
    value: str | None = None
    id: UUID = field(default_factory=uuid4)


@dataclass
class PropertyImage:
    storage_key: str
    url: str | None = None
    thumbnail_url: str | None = None
    caption: str | None = None
    sort_order: int = 0
    is_primary: bool = False
    width: int | None = None
    height: int | None = None
    file_size: int | None = None
    mime_type: str | None = None
    processing_status: ProcessingStatus = ProcessingStatus.PENDING
    id: UUID = field(default_factory=uuid4)
    deleted_at: datetime | None = None


@dataclass
class PropertyVideo:
    storage_key: str
    url: str | None = None
    thumbnail_url: str | None = None
    video_type: str = "standard"
    embed_url: str | None = None
    provider: str | None = None
    duration_seconds: int | None = None
    caption: str | None = None
    sort_order: int = 0
    is_primary: bool = False
    mime_type: str | None = None
    file_size: int | None = None
    processing_status: ProcessingStatus = ProcessingStatus.PENDING
    id: UUID = field(default_factory=uuid4)
    deleted_at: datetime | None = None
