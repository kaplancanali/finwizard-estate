from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any
from uuid import UUID


@dataclass
class SortCriteria:
    field: str
    direction: str = "desc"


@dataclass
class GeoCriteria:
    type: str
    payload: dict[str, Any]


@dataclass
class SearchFilterSet:
    raw: dict[str, Any] = field(default_factory=dict)


@dataclass
class PropertySearchCriteria:
    tenant_id: UUID | None = None
    query: str | None = None
    filters: SearchFilterSet | None = None
    geo: GeoCriteria | None = None
    sort: list[SortCriteria] = field(default_factory=lambda: [SortCriteria(field="created_at", direction="desc")])
    page: int = 1
    page_size: int = 20
    include_facets: bool = False

    @property
    def filters_dict(self) -> dict[str, Any]:
        return self.filters.raw if self.filters else {}

    @property
    def geo_dict(self) -> dict[str, Any] | None:
        return self.geo.payload if self.geo else None

    @property
    def sort_list(self) -> list[dict[str, str]]:
        return [{"field": s.field, "direction": s.direction} for s in self.sort]


@dataclass
class NearbySearchCriteria:
    latitude: float = 0.0
    longitude: float = 0.0
    radius_meters: int = 5000
    limit: int = 20
    property_type: str | None = None
    status: list[str] | None = None


@dataclass
class MapSearchCriteria:
    north: float = 0.0
    south: float = 0.0
    east: float = 0.0
    west: float = 0.0
    zoom: int = 12
    cluster: bool = True
    limit: int = 500


@dataclass
class MapCluster:
    latitude: float
    longitude: float
    count: int
    property_ids: list[str]


@dataclass
class PropertySummary:
    id: UUID | None = None
    property_code: str | None = None
    slug: str | None = None
    title: str | None = None
    property_type: str | None = None
    status: str | None = None
    sale_price: Any = None
    rental_price: Any = None
    currency: str | None = None
    province: str | None = None
    district: str | None = None
    neighborhood: str | None = None
    latitude: Any = None
    longitude: Any = None
    net_area_sqm: Any = None
    room_count: Any = None
    bathroom_count: Any = None
    primary_image_url: str | None = None
    created_at: Any = None
    distance_meters: float | None = None


@dataclass
class PropertySearchResult:
    items: list[PropertySummary]
    total: int
    page: int
    page_size: int
    facets: dict[str, Any] | None = None


@dataclass
class PropertyStatistics:
    total_count: int = 0
    by_status: dict[str, int] = field(default_factory=dict)
    by_type: dict[str, int] = field(default_factory=dict)
    by_province: dict[str, int] = field(default_factory=dict)
    price_stats: dict[str, float | None] = field(default_factory=dict)
    grouped: dict[str, dict[str, int]] = field(default_factory=dict)
