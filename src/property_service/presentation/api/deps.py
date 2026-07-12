from __future__ import annotations

from property_service.application.services.property_application_service import PropertyApplicationService
from property_service.application.services.property_history_service import PropertyHistoryService
from property_service.application.services.property_import_service import PropertyImportService
from property_service.application.services.property_media_service import PropertyMediaService
from property_service.application.services.property_search_service import PropertySearchService
from property_service.application.services.property_statistics_service import PropertyStatisticsService
from property_service.di.container import get_container
from property_service.presentation.security.deps import get_auth_context, require_permission

__all__ = [
    "get_auth_context",
    "get_history_service",
    "get_import_service",
    "get_media_service",
    "get_property_service",
    "get_search_service",
    "get_statistics_service",
    "require_permission",
]


def get_property_service() -> PropertyApplicationService:
    return get_container().property_service


def get_search_service() -> PropertySearchService:
    return get_container().search_service


def get_media_service() -> PropertyMediaService:
    return get_container().media_service


def get_import_service() -> PropertyImportService:
    return get_container().import_service


def get_history_service() -> PropertyHistoryService:
    return get_container().history_service


def get_statistics_service() -> PropertyStatisticsService:
    return get_container().statistics_service
