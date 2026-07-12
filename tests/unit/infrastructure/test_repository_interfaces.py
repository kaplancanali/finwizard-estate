from __future__ import annotations

import inspect
from uuid import uuid4

import pytest

from property_service.application.dto.property_search_dto import (
    MapSearchCriteria,
    NearbySearchCriteria,
    PropertySearchCriteria,
    PropertyStatistics,
    PropertySummary,
)
from property_service.application.ports.idempotency_store import IIdempotencyStore
from property_service.application.ports.object_storage import IObjectStorage
from property_service.application.ports.property_cache import IPropertyCache
from property_service.application.unit_of_work import IUnitOfWork
from property_service.domain.repositories import IOutboxRepository, IPropertyRepository, IPropertySearchRepository
from property_service.domain.repositories.property_version_repository import IPropertyVersionRepository
from property_service.infrastructure.cache.in_memory_property_cache import InMemoryPropertyCache
from property_service.infrastructure.cache.property_cache import RedisPropertyCache
from property_service.infrastructure.cache.redis_idempotency_store import RedisIdempotencyStore
from property_service.infrastructure.persistence.repositories.outbox_repository import SqlAlchemyOutboxRepository
from property_service.infrastructure.persistence.repositories.property_repository import SqlAlchemyPropertyRepository
from property_service.infrastructure.persistence.repositories.search_repository import SqlAlchemySearchRepository
from property_service.infrastructure.storage.s3_storage import S3ObjectStorage
from property_service.shared.idempotency import InMemoryIdempotencyStore


class TestRepositoryInterfaces:
    def test_property_repository_interface_methods(self) -> None:
        methods = {name for name, _ in inspect.getmembers(IPropertyRepository, predicate=inspect.isfunction)}
        assert "get_status_history" in methods
        assert "get_ownership_history" in methods
        assert "get_audit_logs" in methods
        assert "soft_delete" in methods

    def test_search_repository_interface_methods(self) -> None:
        methods = {name for name, _ in inspect.getmembers(IPropertySearchRepository, predicate=inspect.isfunction)}
        assert "find_nearby" in methods
        assert "map_search" in methods
        assert "get_statistics" in methods

    def test_version_repository_has_latest_version(self) -> None:
        assert "get_latest_version_number" in dict(inspect.getmembers(IPropertyVersionRepository))

    def test_unit_of_work_exposes_write_repositories_only(self) -> None:
        annotations = IUnitOfWork.__annotations__
        assert set(annotations) == {"properties", "versions", "outbox"}

    def test_infrastructure_implements_ports(self) -> None:
        assert issubclass(RedisPropertyCache, IPropertyCache)
        assert issubclass(InMemoryPropertyCache, IPropertyCache)
        assert issubclass(S3ObjectStorage, IObjectStorage)
        assert issubclass(RedisIdempotencyStore, IIdempotencyStore)
        assert issubclass(InMemoryIdempotencyStore, IIdempotencyStore)

    def test_sqlalchemy_repositories_implement_domain_interfaces(self) -> None:
        assert issubclass(SqlAlchemyPropertyRepository, IPropertyRepository)
        assert issubclass(SqlAlchemySearchRepository, IPropertySearchRepository)
        assert issubclass(SqlAlchemyOutboxRepository, IOutboxRepository)

    def test_search_dto_types_exist(self) -> None:
        assert PropertySearchCriteria(query="test").page == 1
        assert NearbySearchCriteria().radius_meters == 5000
        assert MapSearchCriteria().cluster is True
        assert PropertyStatistics().total_count == 0
        assert PropertySummary().distance_meters is None

    @pytest.mark.asyncio
    async def test_outbox_get_pending_uses_skip_locked_on_postgres(self) -> None:
        source = inspect.getsource(SqlAlchemyOutboxRepository.get_pending)
        assert "skip_locked=True" in source
