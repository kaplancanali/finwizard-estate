from __future__ import annotations

TASK_ROUTES = {
    "property.image.*": {"queue": "property.image"},
    "property.import.*": {"queue": "property.import"},
    "property.geocoding.*": {"queue": "property.geocoding"},
    "property.sync.*": {"queue": "property.sync"},
    "property.outbox.*": {"queue": "property.outbox"},
    "property.maintenance.*": {"queue": "property.maintenance"},
}

TASK_ANNOTATIONS = {
    "property.image.process_upload": {
        "max_retries": 3,
        "default_retry_delay": 30,
        "soft_time_limit": 120,
    },
    "property.geocoding.forward": {
        "max_retries": 2,
        "rate_limit": "1/s",
    },
    "property.geocoding.reverse": {
        "max_retries": 2,
        "rate_limit": "1/s",
    },
    "property.import.bulk": {
        "soft_time_limit": 1800,
    },
}
