from __future__ import annotations

import logging

from property_service.infrastructure.celery.app import celery_app
from property_service.infrastructure.celery.metrics import record_task_result
from property_service.infrastructure.celery.task_runner import run_async
from property_service.infrastructure.geocoding.nominatim_adapter import NominatimAdapter

logger = logging.getLogger(__name__)


@celery_app.task(name="property.geocoding.forward", bind=True, max_retries=2, rate_limit="1/s")
def forward_geocode(self, property_id: str, address: str = "") -> str:
    try:
        geocoder = NominatimAdapter()
        run_async(geocoder.forward_geocode(address or f"property:{property_id}"))
        record_task_result("property.geocoding.forward", "success")
        return f"forward_geocoded:{property_id}"
    except Exception as exc:
        record_task_result("property.geocoding.forward", "failure")
        raise self.retry(exc=exc, countdown=60)


@celery_app.task(name="property.geocoding.reverse", bind=True, max_retries=2, rate_limit="1/s")
def reverse_geocode(self, property_id: str, latitude: float = 41.0, longitude: float = 29.0) -> str:
    try:
        geocoder = NominatimAdapter()
        run_async(geocoder.reverse_geocode(latitude, longitude))
        record_task_result("property.geocoding.reverse", "success")
        return f"reverse_geocoded:{property_id}"
    except Exception as exc:
        record_task_result("property.geocoding.reverse", "failure")
        raise self.retry(exc=exc, countdown=60)


geocode_property = reverse_geocode

__all__ = ["forward_geocode", "reverse_geocode", "geocode_property"]
