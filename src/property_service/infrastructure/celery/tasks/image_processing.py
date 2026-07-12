from __future__ import annotations

import logging

from property_service.infrastructure.celery.app import celery_app
from property_service.infrastructure.celery.metrics import record_task_result

logger = logging.getLogger(__name__)


@celery_app.task(name="property.image.process_upload", bind=True, max_retries=3, default_retry_delay=30)
def process_image_upload(self, storage_key: str) -> str:
    try:
        logger.info("image_process_started", extra={"storage_key": storage_key})
        record_task_result("property.image.process_upload", "success")
        return f"processed:{storage_key}"
    except Exception as exc:
        record_task_result("property.image.process_upload", "failure")
        logger.exception("image_process_failed", extra={"storage_key": storage_key})
        raise self.retry(exc=exc, countdown=30 * (2 ** self.request.retries))


@celery_app.task(name="property.image.cleanup_orphaned")
def cleanup_orphaned_images() -> str:
    logger.info("cleanup_orphaned_images_started")
    record_task_result("property.image.cleanup_orphaned", "success")
    return "cleanup:0"

__all__ = ["process_image_upload", "cleanup_orphaned_images"]
