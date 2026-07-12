from __future__ import annotations

from uuid import uuid4

import pytest

from property_service.application.auth_context import AuthContext
from property_service.application.services.property_history_service import PropertyHistoryService
from property_service.di.container import build_container
from property_service.infrastructure.cache.property_cache_manager import PropertyCacheManager


@pytest.fixture
def container():
    return build_container()


@pytest.fixture
def auth():
    return AuthContext(user_id=uuid4(), tenant_id=uuid4())


class TestServiceResponsibilities:
    def test_container_wires_all_application_services(self, container) -> None:
        assert container.property_service is not None
        assert container.search_service is not None
        assert container.media_service is not None
        assert container.import_service is not None
        assert container.history_service is not None
        assert container.statistics_service is not None
        assert isinstance(container.cache_manager, PropertyCacheManager)

    def test_handler_registry_exposes_cqrs_handlers(self, container) -> None:
        handlers = container.handlers
        assert handlers.create_property is not None
        assert handlers.restore_property is not None
        assert handlers.get_history is not None
        assert handlers.get_statistics is not None

    def test_search_service_has_read_only_query_methods(self) -> None:
        from property_service.application.services.property_search_service import PropertySearchService
        from property_service.infrastructure.persistence.repositories.search_repository import SqlAlchemySearchRepository

        service = PropertySearchService(lambda: None)
        assert hasattr(service, "search")
        assert hasattr(service, "find_nearby")
        assert hasattr(service, "map_search")
        assert not hasattr(service, "delete_property")
        assert SqlAlchemySearchRepository._cluster_summaries([], 10) == []
