from __future__ import annotations

from property_service.application.queries import (
    GetNearbyPropertiesQuery,
    GetPropertyHistoryQuery,
    GetPropertyQuery,
    GetPropertyStatisticsQuery,
    GetPropertyVersionsQuery,
    SearchPropertiesQuery,
)
from property_service.application.auth_context import AuthContext
from property_service.application.services.property_application_service import PropertyApplicationService
from property_service.application.services.property_history_service import PropertyHistoryService
from property_service.application.services.property_search_service import PropertySearchService
from property_service.application.services.property_statistics_service import PropertyStatisticsService
from property_service.application.dto.property_search_dto import (
    GeoCriteria,
    PropertySearchCriteria,
    SearchFilterSet,
    SortCriteria,
)


class GetPropertyHandler:
    def __init__(self, service: PropertyApplicationService) -> None:
        self._service = service

    async def handle(self, query: GetPropertyQuery, auth: AuthContext):
        return await self._service.get_property(query.property_id, auth)


class SearchPropertiesHandler:
    def __init__(self, service: PropertySearchService) -> None:
        self._service = service

    async def handle(self, query: SearchPropertiesQuery, auth: AuthContext):
        dto = query.criteria
        criteria = PropertySearchCriteria(
            tenant_id=auth.tenant_id,
            query=dto.query,
            filters=SearchFilterSet(raw=dto.filters or {}),
            geo=GeoCriteria(type=dto.geo.get("type", ""), payload=dto.geo) if dto.geo else None,
            sort=[SortCriteria(field="created_at", direction="desc")],
            page=dto.page,
            page_size=dto.page_size,
            include_facets=dto.include_facets,
        )
        return await self._service.search(criteria, auth)


class GetNearbyPropertiesHandler:
    def __init__(self, service: PropertySearchService) -> None:
        self._service = service

    async def handle(self, query: GetNearbyPropertiesQuery, auth: AuthContext):
        return await self._service.find_nearby(
            auth,
            query.latitude,
            query.longitude,
            query.radius_meters,
            limit=query.limit,
        )


class GetPropertyStatisticsHandler:
    def __init__(self, service: PropertyStatisticsService) -> None:
        self._service = service

    async def handle(self, query: GetPropertyStatisticsQuery, auth: AuthContext):
        return await self._service.get_tenant_statistics(auth)


class GetPropertyHistoryHandler:
    def __init__(self, service: PropertyHistoryService) -> None:
        self._service = service

    async def handle(self, query: GetPropertyHistoryQuery, auth: AuthContext):
        if query.history_type == "status":
            return await self._service.get_status_history(
                query.property_id, auth, page=query.page, page_size=query.page_size
            )
        if query.history_type == "ownership":
            return await self._service.get_ownership_history(
                query.property_id, auth, page=query.page, page_size=query.page_size
            )
        return await self._service.get_price_history(
            query.property_id, auth, page=query.page, page_size=query.page_size
        )


class GetPropertyVersionsHandler:
    def __init__(self, service: PropertyHistoryService) -> None:
        self._service = service

    async def handle(self, query: GetPropertyVersionsQuery, auth: AuthContext):
        return await self._service.get_versions(
            query.property_id, auth, page=query.page, page_size=query.page_size
        )
