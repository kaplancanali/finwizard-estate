from __future__ import annotations

import logging

from property_service.domain.events.base import DomainEvent
from property_service.infrastructure.cache.property_cache_manager import PropertyCacheManager

logger = logging.getLogger(__name__)


async def handle_domain_event(event: DomainEvent, cache_manager: PropertyCacheManager | None = None) -> None:
    """Internal side-effects for domain events (audit, cache invalidation hooks)."""
    logger.debug("domain_event_received", extra={"event_type": type(event).__name__})
    if cache_manager and event.aggregate_id and event.tenant_id:
        await cache_manager.on_property_changed(event.aggregate_id, event.tenant_id)
