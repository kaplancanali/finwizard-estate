"""Re-export search read models from domain for application-layer callers."""

from property_service.domain.queries.search_criteria import (
    GeoCriteria,
    MapCluster,
    MapSearchCriteria,
    NearbySearchCriteria,
    PropertySearchCriteria,
    PropertySearchResult,
    PropertyStatistics,
    PropertySummary,
    SearchFilterSet,
    SortCriteria,
)

PropertySearchDTO = PropertySearchCriteria

__all__ = [
    "GeoCriteria",
    "MapCluster",
    "MapSearchCriteria",
    "NearbySearchCriteria",
    "PropertySearchCriteria",
    "PropertySearchDTO",
    "PropertySearchResult",
    "PropertyStatistics",
    "PropertySummary",
    "SearchFilterSet",
    "SortCriteria",
]
