from __future__ import annotations

import logging
from uuid import UUID

from property_service.infrastructure.celery.app import celery_app
from property_service.infrastructure.celery.metrics import record_task_result
from property_service.infrastructure.celery.task_runner import run_async

logger = logging.getLogger(__name__)


@celery_app.task(name="property.import.bulk", soft_time_limit=1800)
def bulk_import(job_id: str) -> str:
    try:
        from property_service.di.container import get_container

        result = run_async(get_container().import_service.process_bulk_import_job(UUID(job_id)))
        record_task_result("property.import.bulk", "success")
        return result
    except Exception:
        record_task_result("property.import.bulk", "failure")
        logger.exception("bulk_import_task_failed", extra={"job_id": job_id})
        raise


@celery_app.task(name="property.import.from_listing_url")
def import_from_listing_url(
    url: str,
    tenant_id: str,
    user_id: str,
    *,
    title: str | None = None,
) -> str:
    try:
        from property_service.application.auth_context import AuthContext
        from property_service.di.container import get_container

        auth = AuthContext(tenant_id=UUID(tenant_id), user_id=UUID(user_id))
        property_obj = run_async(
            get_container().import_service.import_from_listing_url(url, auth, title=title)
        )
        record_task_result("property.import.from_listing_url", "success")
        return f"imported:{property_obj.id}"
    except Exception:
        record_task_result("property.import.from_listing_url", "failure")
        logger.exception("listing_url_import_failed", extra={"url": url})
        raise


import_properties = bulk_import

__all__ = ["bulk_import", "import_from_listing_url", "import_properties"]
