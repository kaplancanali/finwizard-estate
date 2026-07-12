from __future__ import annotations

import logging
from uuid import UUID

from property_service.infrastructure.celery.app import celery_app
from property_service.infrastructure.celery.metrics import record_task_result
from property_service.infrastructure.celery.task_runner import run_async

logger = logging.getLogger(__name__)


@celery_app.task(name="property.sync.listing")
def sync_listings() -> str:
    logger.info("scheduled_listing_sync_started")
    record_task_result("property.sync.listing", "success")
    return "sync_scheduled:0"


@celery_app.task(name="property.sync.listing_single")
def sync_listing_single(property_id: str) -> str:
    try:
        from property_service.application.auth_context import AuthContext
        from property_service.di.container import get_container
        from property_service.infrastructure.persistence.unit_of_work import unit_of_work

        async def _run() -> str:
            async with unit_of_work() as uow:
                prop = await uow.properties.get_by_id(UUID(property_id))
            if prop is None:
                return f"not_found:{property_id}"
            auth = AuthContext(tenant_id=prop.tenant_id, user_id=prop.tenant_id)
            return await get_container().import_service.sync_listing_inline(UUID(property_id), auth)

        result = run_async(_run())
        record_task_result("property.sync.listing_single", "success")
        return result
    except Exception:
        record_task_result("property.sync.listing_single", "failure")
        logger.exception("listing_single_sync_failed", extra={"property_id": property_id})
        raise


sync_listing = sync_listing_single

__all__ = ["sync_listings", "sync_listing_single", "sync_listing"]
