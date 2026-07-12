from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from property_service.application.handlers.handler_registry import HandlerRegistry
from property_service.application.handlers.command_handlers import (
    ChangePropertyStatusHandler,
    CreatePropertyHandler,
    DeletePropertyHandler,
    RegisterFromSourceHandler,
    RestorePropertyHandler,
    UpdatePropertyHandler,
)
from property_service.application.handlers.query_handlers import (
    GetNearbyPropertiesHandler,
    GetPropertyHandler,
    GetPropertyHistoryHandler,
    GetPropertyStatisticsHandler,
    GetPropertyVersionsHandler,
    SearchPropertiesHandler,
)
from property_service.application.services.property_application_service import PropertyApplicationService
from property_service.application.services.property_history_service import PropertyHistoryService
from property_service.application.services.property_import_service import PropertyImportService
from property_service.application.services.property_media_service import PropertyMediaService
from property_service.application.services.property_search_service import PropertySearchService
from property_service.application.services.property_statistics_service import PropertyStatisticsService
from property_service.infrastructure.cache.in_memory_property_cache import InMemoryPropertyCache
from property_service.infrastructure.cache.property_cache import RedisPropertyCache
from property_service.infrastructure.cache.property_cache_manager import PropertyCacheManager
from property_service.config import get_settings
from property_service.infrastructure.geocoding.nominatim_adapter import NominatimAdapter
from property_service.infrastructure.listing.listing_adapter import StubListingAdapter
from property_service.infrastructure.messaging.outbox_processor import OutboxProcessor
from property_service.infrastructure.messaging.rabbitmq_publisher import RabbitMQPublisher
from property_service.infrastructure.persistence.unit_of_work import unit_of_work
from property_service.infrastructure.persistence.read_unit_of_work import search_unit_of_work
from property_service.infrastructure.storage.s3_storage import S3ObjectStorage


@dataclass
class Container:
    uow_factory: Callable
    property_service: PropertyApplicationService
    search_service: PropertySearchService
    media_service: PropertyMediaService
    import_service: PropertyImportService
    history_service: PropertyHistoryService
    statistics_service: PropertyStatisticsService
    cache_manager: PropertyCacheManager
    handlers: HandlerRegistry
    geocoder: NominatimAdapter
    storage: S3ObjectStorage
    outbox_processor: OutboxProcessor
    publisher: RabbitMQPublisher


_container: Container | None = None


def build_container() -> Container:
    settings = get_settings()
    property_cache = InMemoryPropertyCache() if settings.cache_backend == "memory" else RedisPropertyCache()
    cache_manager = PropertyCacheManager(property_cache)
    storage = S3ObjectStorage()

    property_service = PropertyApplicationService(unit_of_work, cache_manager=cache_manager)
    search_service = PropertySearchService(search_unit_of_work, property_cache=property_cache)
    history_service = PropertyHistoryService(unit_of_work)
    statistics_service = PropertyStatisticsService(search_unit_of_work, cache_manager=cache_manager)
    media_service = PropertyMediaService(unit_of_work, storage, cache_manager=cache_manager)
    import_service = PropertyImportService(
        property_service,
        unit_of_work,
        listing_adapter=StubListingAdapter(),
    )

    handlers = HandlerRegistry(
        create_property=CreatePropertyHandler(property_service),
        update_property=UpdatePropertyHandler(property_service),
        delete_property=DeletePropertyHandler(property_service),
        restore_property=RestorePropertyHandler(property_service),
        change_status=ChangePropertyStatusHandler(property_service),
        register_from_source=RegisterFromSourceHandler(property_service),
        get_property=GetPropertyHandler(property_service),
        search_properties=SearchPropertiesHandler(search_service),
        get_nearby=GetNearbyPropertiesHandler(search_service),
        get_statistics=GetPropertyStatisticsHandler(statistics_service),
        get_history=GetPropertyHistoryHandler(history_service),
        get_versions=GetPropertyVersionsHandler(history_service),
    )

    return Container(
        uow_factory=unit_of_work,
        property_service=property_service,
        search_service=search_service,
        media_service=media_service,
        import_service=import_service,
        history_service=history_service,
        statistics_service=statistics_service,
        cache_manager=cache_manager,
        handlers=handlers,
        geocoder=NominatimAdapter(),
        storage=storage,
        outbox_processor=OutboxProcessor(),
        publisher=RabbitMQPublisher(),
    )


def get_container() -> Container:
    global _container
    if _container is None:
        _container = build_container()
    return _container


def reset_container() -> None:
    global _container
    _container = None
