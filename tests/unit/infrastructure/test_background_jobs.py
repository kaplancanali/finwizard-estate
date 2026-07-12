from __future__ import annotations

from uuid import uuid4

import pytest

from property_service.infrastructure.celery.app import celery_app
from property_service.infrastructure.celery.beat_schedule import beat_schedule
from property_service.infrastructure.celery.config import TASK_ROUTES
from property_service.infrastructure.celery.metrics import get_task_counters, record_task_result, reset_task_counters
from property_service.infrastructure.jobs.import_job_store import (
    BulkImportJobRecord,
    InMemoryImportJobStore,
    utcnow,
)


class TestCeleryConfiguration:
    def test_task_routes_match_doc_topology(self) -> None:
        assert TASK_ROUTES["property.outbox.*"]["queue"] == "property.outbox"
        assert TASK_ROUTES["property.import.*"]["queue"] == "property.import"
        assert TASK_ROUTES["property.image.*"]["queue"] == "property.image"

    def test_celery_ack_and_prefetch_settings(self) -> None:
        assert celery_app.conf.task_acks_late is True
        assert celery_app.conf.worker_prefetch_multiplier == 1

    def test_registered_task_names(self) -> None:
        names = {
            "property.outbox.publish",
            "property.image.process_upload",
            "property.image.cleanup_orphaned",
            "property.geocoding.forward",
            "property.geocoding.reverse",
            "property.import.bulk",
            "property.import.from_listing_url",
            "property.sync.listing",
            "property.sync.listing_single",
            "property.maintenance.refresh_statistics",
            "property.maintenance.purge_outbox",
            "property.maintenance.create_version_snapshot",
            "property.maintenance.update_search_vector",
        }
        registered = set(celery_app.tasks.keys())
        assert names.issubset(registered)


class TestBeatScheduleCatalog:
    def test_all_doc_schedules_defined(self) -> None:
        assert set(beat_schedule) == {
            "publish-outbox",
            "refresh-statistics",
            "sync-listings",
            "cleanup-orphaned-images",
            "purge-outbox",
        }


class TestImportJobStore:
    @pytest.mark.asyncio
    async def test_create_get_and_update_job(self) -> None:
        store = InMemoryImportJobStore()
        job_id = uuid4()
        tenant_id = uuid4()
        user_id = uuid4()
        record = BulkImportJobRecord(
            job_id=job_id,
            type="bulk_import",
            status="queued",
            total_items=2,
            tenant_id=tenant_id,
            user_id=user_id,
            source_type="manual",
            items_payload=[{"title": "A"}, {"title": "B"}],
            started_at=utcnow(),
            updated_at=utcnow(),
        )
        await store.create(record)
        loaded = await store.get(job_id)
        assert loaded is not None
        assert loaded.status == "queued"
        assert loaded.total_items == 2

        loaded.processed = 1
        loaded.status = "processing"
        await store.save(loaded)
        updated = await store.get(job_id)
        assert updated is not None
        assert updated.processed == 1
        assert updated.status == "processing"


class TestCeleryMetrics:
    def test_record_task_result(self) -> None:
        reset_task_counters()
        record_task_result("property.import.bulk", "success")
        counters = get_task_counters()
        assert counters["property.import.bulk:success"] == 1
