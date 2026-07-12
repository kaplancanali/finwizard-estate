"""Query objects — CQRS read-side entry points."""

from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID

from property_service.application.dto.property_search_dto import PropertySearchDTO


@dataclass(frozen=True)
class GetPropertyQuery:
    property_id: UUID


@dataclass(frozen=True)
class SearchPropertiesQuery:
    criteria: PropertySearchDTO


@dataclass(frozen=True)
class GetNearbyPropertiesQuery:
    latitude: float
    longitude: float
    radius_meters: int = 5000
    limit: int = 20


@dataclass(frozen=True)
class GetPropertyHistoryQuery:
    property_id: UUID
    history_type: str = "price"
    page: int = 1
    page_size: int = 20


@dataclass(frozen=True)
class GetPropertyVersionsQuery:
    property_id: UUID
    page: int = 1
    page_size: int = 20


@dataclass(frozen=True)
class GetPropertyStatisticsQuery:
    tenant_id: UUID | None = None
