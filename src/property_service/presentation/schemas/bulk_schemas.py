from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from property_service.domain.enums.property_status import PropertyStatus
from property_service.domain.enums.source_type import SourceType
from property_service.presentation.schemas.property_schemas import PropertyCreateRequest


class BulkImportOptions(BaseModel):
    async_mode: bool = Field(True, alias="async")
    skip_duplicates: bool = True
    default_status: PropertyStatus = PropertyStatus.DRAFT
    auto_geocode: bool = True

    model_config = {"populate_by_name": True}


BulkImportItem = PropertyCreateRequest


class BulkError(BaseModel):
    index: int
    message: str
    code: str | None = None


class BulkImportRequest(BaseModel):
    source_type: SourceType
    items: list[BulkImportItem] = Field(..., min_length=1, max_length=500)
    options: BulkImportOptions = Field(default_factory=BulkImportOptions)


class BulkUpdateRequest(BaseModel):
    filter: dict[str, object]
    updates: dict[str, object]
    options: dict[str, object] | None = None


class BulkDeleteRequest(BaseModel):
    property_ids: list[UUID] = Field(..., min_length=1, max_length=100)
    options: dict[str, object] | None = None


class BulkJobResponse(BaseModel):
    job_id: UUID
    status: str
    total_items: int
    processed: int = 0
    created: int = 0
    skipped: int = 0
    failed: int = 0
    errors: list[BulkError] = Field(default_factory=list)
    started_at: datetime | None = None
    completed_at: datetime | None = None
