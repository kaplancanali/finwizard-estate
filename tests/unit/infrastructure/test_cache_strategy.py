from __future__ import annotations

from uuid import uuid4

import pytest

from property_service.application.dto.property_search_dto import PropertySearchCriteria
from property_service.domain.events.property_created import PropertyCreated
from property_service.domain.events.property_deleted import PropertyDeleted
from property_service.domain.events.property_location_changed import PropertyLocationChanged
from property_service.domain.events.property_price_changed import PropertyPriceChanged
from property_service.infrastructure.cache.cache_config import (
    hash_search_criteria,
    lookup_types_key,
    property_detail_key,
    property_stats_key,
    search_cache_key,
)
from property_service.infrastructure.cache.geohash_utils import encode_geohash, geohash_neighbors
from property_service.infrastructure.cache.in_memory_property_cache import InMemoryPropertyCache
from property_service.infrastructure.cache.property_cache_manager import PropertyCacheManager


class TestCacheKeys:
    def test_search_cache_key_is_stable(self) -> None:
        criteria = PropertySearchCriteria(query="apartment", page=1, page_size=20)
        digest = hash_search_criteria(criteria)
        key = search_cache_key(uuid4(), digest)
        assert key.startswith("property:search:")

    def test_geohash_neighbors_include_center(self) -> None:
        cell = encode_geohash(41.0, 29.0)
        neighbors = geohash_neighbors(cell)
        assert cell in neighbors


class TestInMemoryPropertyCache:
    @pytest.mark.asyncio
    async def test_cache_aside_round_trip(self) -> None:
        cache = InMemoryPropertyCache()
        property_id = uuid4()
        await cache.set_property(property_id, {"title": "Cached"})
        loaded = await cache.get_property(property_id)
        assert loaded == {"title": "Cached"}

    @pytest.mark.asyncio
    async def test_invalidate_property_removes_detail_and_metadata(self) -> None:
        cache = InMemoryPropertyCache()
        property_id = uuid4()
        await cache.set_property(property_id, {"title": "x"})
        await cache.set_metadata(property_id, {"custom_field": "y"})
        await cache.invalidate_property(property_id)
        assert await cache.get_property(property_id) is None
        assert await cache.get_metadata(property_id) is None

    @pytest.mark.asyncio
    async def test_stampede_lock(self) -> None:
        cache = InMemoryPropertyCache()
        assert await cache.try_acquire_lock("lock:test") is True
        assert await cache.try_acquire_lock("lock:test") is False
        await cache.release_lock("lock:test")
        assert await cache.try_acquire_lock("lock:test") is True


class TestPropertyCacheManager:
    @pytest.mark.asyncio
    async def test_property_created_invalidates_stats_only(self) -> None:
        backend = InMemoryPropertyCache()
        manager = PropertyCacheManager(backend)
        tenant_id = uuid4()
        await backend.set_statistics(tenant_id, {"total": 1}, ttl=60)
        event = PropertyCreated(tenant_id=tenant_id, aggregate_id=uuid4())
        from property_service.domain.aggregates.property import Property
        from property_service.domain.entities.property_location import PropertyLocation
        from property_service.domain.entities.property_version import PropertyExternalSource
        from property_service.domain.enums.property_category import PropertyCategory
        from property_service.domain.enums.property_type import PropertyType
        from property_service.domain.enums.source_type import SourceType
        from property_service.domain.value_objects.property_classification import PropertyClassification
        from property_service.domain.value_objects.property_code import PropertyCode
        from property_service.domain.value_objects.slug import Slug

        prop = Property.create(
            tenant_id=tenant_id,
            property_code=PropertyCode("FW-TR-IST-00000200"),
            slug=Slug("cache-test"),
            title="Cache",
            classification=PropertyClassification(PropertyType.APARTMENT, PropertyCategory.RESIDENTIAL),
            location=PropertyLocation(country_code="TR", province="Istanbul"),
            created_by=uuid4(),
            source=PropertyExternalSource(source_type=SourceType.MANUAL),
        )
        await manager.handle_domain_events([event], prop)
        assert await backend.get_statistics(tenant_id) is None

    @pytest.mark.asyncio
    async def test_get_property_detail_cached_uses_loader_once(self) -> None:
        backend = InMemoryPropertyCache()
        manager = PropertyCacheManager(backend)
        property_id = uuid4()
        calls = {"count": 0}

        async def loader() -> dict:
            calls["count"] += 1
            return {"id": str(property_id)}

        first = await manager.get_property_detail_cached(property_id, loader)
        second = await manager.get_property_detail_cached(property_id, loader)
        assert first == second
        assert calls["count"] == 1
        assert manager.metrics["hits"] >= 1

    @pytest.mark.asyncio
    async def test_warm_lookup_caches(self) -> None:
        backend = InMemoryPropertyCache()
        manager = PropertyCacheManager(backend)
        await manager.warm_lookup_caches()
        assert await backend.get_lookup(lookup_types_key()) is not None

    @pytest.mark.asyncio
    async def test_location_change_invalidates_nearby(self) -> None:
        backend = InMemoryPropertyCache()
        manager = PropertyCacheManager(backend)
        tenant_id = uuid4()
        geohash = encode_geohash(41.0, 29.0)
        key = backend.nearby_cache_key(tenant_id, geohash, 5000)
        await backend.set_nearby(key, {"items": []}, ttl=60)
        event = PropertyLocationChanged(
            tenant_id=tenant_id,
            aggregate_id=uuid4(),
            new_location={"latitude": 41.0, "longitude": 29.0},
        )
        from property_service.domain.aggregates.property import Property
        from property_service.domain.entities.property_location import PropertyLocation
        from property_service.domain.entities.property_version import PropertyExternalSource
        from property_service.domain.enums.property_category import PropertyCategory
        from property_service.domain.enums.property_type import PropertyType
        from property_service.domain.enums.source_type import SourceType
        from property_service.domain.value_objects.property_classification import PropertyClassification
        from property_service.domain.value_objects.property_code import PropertyCode
        from property_service.domain.value_objects.slug import Slug

        prop = Property.create(
            tenant_id=tenant_id,
            property_code=PropertyCode("FW-TR-IST-00000201"),
            slug=Slug("nearby-cache"),
            title="Nearby",
            classification=PropertyClassification(PropertyType.APARTMENT, PropertyCategory.RESIDENTIAL),
            location=PropertyLocation(country_code="TR", province="Istanbul"),
            created_by=uuid4(),
            source=PropertyExternalSource(source_type=SourceType.MANUAL),
        )
        await manager.handle_domain_events([event], prop)
        assert await backend.get_nearby(key) is None
