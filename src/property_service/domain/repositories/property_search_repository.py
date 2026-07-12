from __future__ import annotations

from abc import ABC, abstractmethod
from uuid import UUID

from property_service.domain.queries.search_criteria import (
    MapCluster,
    MapSearchCriteria,
    NearbySearchCriteria,
    PropertySearchCriteria,
    PropertySearchResult,
    PropertyStatistics,
    PropertySummary,
)


class IPropertySearchRepository(ABC):
    @abstractmethod
    async def search(
        self,
        criteria: PropertySearchCriteria,
        tenant_id: UUID,
    ) -> PropertySearchResult: ...

    @abstractmethod
    async def find_nearby(
        self,
        criteria: NearbySearchCriteria,
        tenant_id: UUID,
    ) -> PropertySearchResult: ...

    @abstractmethod
    async def map_search(
        self,
        criteria: MapSearchCriteria,
        tenant_id: UUID,
    ) -> list[MapCluster | PropertySummary]: ...

    @abstractmethod
    async def get_statistics(
        self,
        tenant_id: UUID,
        *,
        group_by: list[str] | None = None,
    ) -> PropertyStatistics: ...

    @abstractmethod
    async def count_by_tenant(self, tenant_id: UUID) -> int: ...

    async def price_distribution(self, tenant_id: UUID) -> dict:
        raise NotImplementedError
