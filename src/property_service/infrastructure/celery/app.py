from __future__ import annotations

from celery import Celery

from property_service.config import get_settings
from property_service.infrastructure.celery.beat_schedule import beat_schedule
from property_service.infrastructure.celery.config import TASK_ANNOTATIONS, TASK_ROUTES

settings = get_settings()

celery_app = Celery("property_service", broker=settings.rabbitmq_url, backend=settings.redis_url)
celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    task_track_started=True,
    task_acks_late=True,
    worker_prefetch_multiplier=1,
    task_default_queue="property.default",
    task_routes=TASK_ROUTES,
    task_annotations=TASK_ANNOTATIONS,
    beat_schedule=beat_schedule,
)

celery_app.autodiscover_tasks(["property_service.infrastructure.celery.tasks"])

# Eager import so task decorators register when the app module loads.
import property_service.infrastructure.celery.tasks  # noqa: F401
