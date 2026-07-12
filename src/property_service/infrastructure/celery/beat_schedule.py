from __future__ import annotations

from celery.schedules import crontab

from property_service.domain.events.catalog import OUTBOX_BATCH_SIZE

beat_schedule = {
    "publish-outbox": {
        "task": "property.outbox.publish",
        "schedule": 5.0,
        "kwargs": {"batch_size": OUTBOX_BATCH_SIZE},
        "options": {"queue": "property.outbox"},
    },
    "refresh-statistics": {
        "task": "property.maintenance.refresh_statistics",
        "schedule": crontab(minute="*/30"),
        "options": {"queue": "property.maintenance"},
    },
    "sync-listings": {
        "task": "property.sync.listing",
        "schedule": crontab(hour="*/6"),
        "options": {"queue": "property.sync"},
    },
    "cleanup-orphaned-images": {
        "task": "property.image.cleanup_orphaned",
        "schedule": crontab(hour=3, minute=0),
        "options": {"queue": "property.maintenance"},
    },
    "purge-outbox": {
        "task": "property.maintenance.purge_outbox",
        "schedule": crontab(hour=4, minute=0),
        "options": {"queue": "property.maintenance"},
    },
}
