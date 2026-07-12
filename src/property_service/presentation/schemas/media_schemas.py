from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from property_service.domain.enums.document_type import DocumentType
from property_service.presentation.schemas.property_schemas import ImageResponse


class ImageUploadRequest(BaseModel):
    file_name: str = Field(..., max_length=255)
    mime_type: str = Field(..., pattern=r"^image/(jpeg|png|webp|gif)$")
    file_size: int = Field(..., gt=0, le=20_971_520)
    caption: str | None = Field(None, max_length=500)
    is_primary: bool = False
    sort_order: int = 0


class ImageUploadResponse(BaseModel):
    image: ImageResponse
    upload_url: str
    expires_at: datetime | None = None


class DocumentUploadRequest(BaseModel):
    file_name: str = Field(..., max_length=255)
    mime_type: str = Field(..., max_length=100)
    file_size: int = Field(..., gt=0, le=52_428_800)
    document_type: DocumentType


class ImageReorderRequest(BaseModel):
    image_ids: list[UUID]
