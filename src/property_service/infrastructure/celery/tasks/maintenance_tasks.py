from __future__ import annotations

import logging

from sqlalchemy import delete, select

from property_service.infrastructure.celery.app import celery_app
from property_service.infrastructure.celery.metrics import record_task_result
from property_service.infrastructure.celery.task_runner import run_async
from property_service.infrastructure.persistence.models import OutboxEventModel, PropertyModel
from property_service.infrastructure.persistence.unit_of_work import unit_of_work

logger = logging.getLogger(__name__)


@celery_app.task(name="property.maintenance.refresh_statistics")
def refresh_statistics() -> str:
    async def _run() -> int:
        from property_service.application.auth_context import AuthContext
        from property_service.di.container import get_container

        container = get_container()
        refreshed = 0
        async with unit_of_work() as uow:
            tenant_ids = (
                await uow.session.execute(select(PropertyModel.tenant_id).distinct())
            ).scalars().all()
        for tenant_id in tenant_ids:
            auth = AuthContext(tenant_id=tenant_id, user_id=tenant_id)
            await container.statistics_service.get_tenant_statistics(auth)
            refreshed += 1
        return refreshed

    count = run_async(_run())
    record_task_result("property.maintenance.refresh_statistics", "success")
    return f"refreshed:{count}"


@celery_app.task(name="property.maintenance.purge_outbox")
def purge_outbox(*, retention_days: int = 7) -> str:
    async def _run() -> int:
        from datetime import datetime, timedelta, timezone

        cutoff = datetime.now(timezone.utc) - timedelta(days=retention_days)
        async with unit_of_work() as uow:
            result = await uow.session.execute(
                delete(OutboxEventModel).where(
                    OutboxEventModel.status == "published",
                    OutboxEventModel.published_at.is_not(None),
                    OutboxEventModel.published_at < cutoff,
                )
            )
            return int(result.rowcount or 0)

    deleted = run_async(_run())
    record_task_result("property.maintenance.purge_outbox", "success")
    return f"purged:{deleted}"


@celery_app.task(name="property.maintenance.create_version_snapshot")
def create_version_snapshot(property_id: str, change_summary: str = "background snapshot") -> str:
    logger.info(
        "create_version_snapshot_queued",
        extra={"property_id": property_id, "change_summary": change_summary},
    )
    record_task_result("property.maintenance.create_version_snapshot", "success")
    return f"snapshot:{property_id}"


@celery_app.task(name="property.maintenance.update_search_vector")
def update_search_vector(property_id: str) -> str:
    logger.info("update_search_vector_queued", extra={"property_id": property_id})
    record_task_result("property.maintenance.update_search_vector", "success")
    return f"search_vector:{property_id}"

__all__ = [
    "refresh_statistics",
    "purge_outbox",
    "create_version_snapshot",
    "update_search_vector",
]
