"""Command objects — CQRS write-side entry points."""

from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID

from property_service.application.dto.property_create_dto import PropertyCreateDTO
from property_service.application.dto.property_update_dto import PropertyUpdateDTO
from property_service.domain.enums.property_status import PropertyStatus


@dataclass(frozen=True)
class CreatePropertyCommand:
    data: PropertyCreateDTO


@dataclass(frozen=True)
class UpdatePropertyCommand:
    property_id: UUID
    data: PropertyUpdateDTO


@dataclass(frozen=True)
class DeletePropertyCommand:
    property_id: UUID


@dataclass(frozen=True)
class BulkImportPropertiesCommand:
    source_type: str
    items: list[dict[str, object]]


@dataclass(frozen=True)
class BulkUpdatePropertiesCommand:
    property_ids: list[UUID]
    changes: dict[str, object]


@dataclass(frozen=True)
class BulkDeletePropertiesCommand:
    property_ids: list[UUID]


@dataclass(frozen=True)
class ChangePropertyStatusCommand:
    property_id: UUID
    status: PropertyStatus
    expected_version: int
    reason: str | None = None


@dataclass(frozen=True)
class UpdatePropertyImagesCommand:
    property_id: UUID
    action: str
    image_ids: list[UUID] | None = None


@dataclass(frozen=True)
class UpdatePropertyDocumentsCommand:
    property_id: UUID
    action: str
    document_ids: list[UUID] | None = None


@dataclass(frozen=True)
class RestorePropertyCommand:
    property_id: UUID


@dataclass(frozen=True)
class RegisterFromSourceCommand:
    data: PropertyCreateDTO
