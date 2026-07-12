from __future__ import annotations

from decimal import Decimal
from typing import Annotated, Any, Literal, Union

from pydantic import BaseModel, Field, model_validator
from typing_extensions import Self

from property_service.domain.enums.property_category import PropertyCategory
from property_service.domain.enums.property_status import PropertyStatus
from property_service.domain.enums.property_type import PropertyType
from property_service.domain.enums.source_type import SourceType
from property_service.presentation.schemas.common import PaginationInput
from property_service.presentation.schemas.property_schemas import PropertyCreateRequest


class RangeFilter(BaseModel):
    min: Decimal | int | None = None
    max: Decimal | int | None = None


class GeoRadiusFilter(BaseModel):
    type: Literal["radius"] = "radius"
    latitude: Decimal = Field(..., ge=-90, le=90)
    longitude: Decimal = Field(..., ge=-180, le=180)
    radius_meters: int = Field(..., gt=0, le=100_000)


class GeoBoundingBoxFilter(BaseModel):
    type: Literal["bounding_box"] = "bounding_box"
    north: Decimal
    south: Decimal
    east: Decimal
    west: Decimal


class GeoPolygonFilter(BaseModel):
    type: Literal["polygon"] = "polygon"
    coordinates: list[list[Decimal]]

    @model_validator(mode="after")
    def validate_polygon(self) -> Self:
        if not self.coordinates:
            raise ValueError("Polygon coordinates required")
        if len(self.coordinates) > 1000:
            raise ValueError("Polygon cannot exceed 1000 points")
        for index, point in enumerate(self.coordinates):
            if len(point) < 2:
                raise ValueError(f"Polygon point {index} must have latitude and longitude")
            lat, lng = point[0], point[1]
            if lat < -90 or lat > 90:
                raise ValueError(f"Polygon latitude out of bounds at index {index}")
            if lng < -180 or lng > 180:
                raise ValueError(f"Polygon longitude out of bounds at index {index}")
        return self


GeoFilter = Annotated[
    Union[GeoRadiusFilter, GeoBoundingBoxFilter, GeoPolygonFilter],
    Field(discriminator="type"),
]


class SearchFilters(BaseModel):
    property_types: list[PropertyType] | None = None
    property_categories: list[PropertyCategory] | None = None
    status: list[PropertyStatus] | None = None
    sale_price: RangeFilter | None = None
    rental_price: RangeFilter | None = None
    net_area_sqm: RangeFilter | None = None
    room_count: RangeFilter | None = None
    bathroom_count: RangeFilter | None = None
    construction_year: RangeFilter | None = None
    country_code: str | None = None
    provinces: list[str] | None = None
    districts: list[str] | None = None
    heating_types: list[str] | None = None
    amenities: list[str] | None = None
    features: dict[str, bool] | None = None
    tags: list[str] | None = None


class SortField(BaseModel):
    field: str
    direction: Literal["asc", "desc"] = "asc"


class PropertySearchRequest(BaseModel):
    query: str | None = Field(None, max_length=500)
    filters: SearchFilters | None = None
    geo: GeoFilter | None = None
    sort: list[SortField] = Field(default_factory=lambda: [SortField(field="created_at", direction="desc")])
    pagination: PaginationInput = Field(default_factory=PaginationInput)
    include_facets: bool = False

    @property
    def page(self) -> int:
        return self.pagination.page

    @property
    def page_size(self) -> int:
        return self.pagination.page_size

    def filters_dict(self) -> dict[str, Any]:
        if not self.filters:
            return {}
        data = self.filters.model_dump(exclude_none=True)
        if types := data.get("property_types"):
            data["property_types"] = [t.value if hasattr(t, "value") else t for t in types]
        if categories := data.get("property_categories"):
            data["property_categories"] = [c.value if hasattr(c, "value") else c for c in categories]
        if statuses := data.get("status"):
            data["status"] = [s.value if hasattr(s, "value") else s for s in statuses]
        for key in ("sale_price", "rental_price", "net_area_sqm", "room_count", "bathroom_count", "construction_year"):
            if key in data and data[key] is not None:
                data[key] = data[key]
        return data

    def geo_dict(self) -> dict[str, Any] | None:
        if not self.geo:
            return None
        return self.geo.model_dump()

    def sort_list(self) -> list[dict[str, str]]:
        return [item.model_dump() for item in self.sort]


SearchRequest = PropertySearchRequest


class RegisterPropertyRequest(BaseModel):
    source_type: SourceType
    source_reference: str | None = None
    title: str | None = Field(None, min_length=3, max_length=500)
    property_type: PropertyType | None = None
    property_category: PropertyCategory | None = None
    location: dict[str, Any] | None = None
    options: dict[str, Any] | None = None

    @model_validator(mode="after")
    def validate_source(self) -> Self:
        if self.source_type == SourceType.LISTING_URL and not self.source_reference:
            raise ValueError("source_reference required for listing_url source")
        return self
