from __future__ import annotations

import logging

from property_service.domain.events.catalog import OUTBOX_BATCH_SIZE
from property_service.infrastructure.celery.app import celery_app
from property_service.infrastructure.celery.metrics import record_task_result
from property_service.infrastructure.celery.task_runner import run_async
from property_service.infrastructure.messaging.outbox_processor import OutboxProcessor

logger = logging.getLogger(__name__)


@celery_app.task(name="property.outbox.publish")
def publish_outbox(batch_size: int = OUTBOX_BATCH_SIZE) -> str:
    try:
        count = run_async(OutboxProcessor().process_batch(batch_size=batch_size))
        record_task_result("property.outbox.publish", "success")
        return f"published:{count}"
    except Exception:
        record_task_result("property.outbox.publish", "failure")
        logger.exception("outbox_publish_task_failed")
        raise


publish_outbox_batch = publish_outbox

__all__ = ["publish_outbox", "publish_outbox_batch"]
