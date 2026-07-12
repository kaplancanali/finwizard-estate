from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from datetime import datetime, timedelta, timezone
from typing import Protocol
from uuid import UUID

from property_service.config import get_settings
from property_service.infrastructure.cache.redis_client import get_redis_client

JOB_TTL_SECONDS = 7 * 24 * 60 * 60
MAX_BULK_IMPORT_ITEMS = 10_000


@dataclass
class BulkImportJobError:
    index: int
    message: str
    source_reference: str | None = None
    code: str | None = None


@dataclass
class BulkImportJobRecord:
    job_id: UUID
    type: str
    status: str
    total_items: int
    tenant_id: UUID
    user_id: UUID
    source_type: str
    items_payload: list[dict]
    processed: int = 0
    created: int = 0
    skipped: int = 0
    failed: int = 0
    errors: list[BulkImportJobError] = field(default_factory=list)
    skip_duplicates: bool = True
    auto_geocode: bool = True
    default_status: str = "draft"
    started_at: datetime | None = None
    completed_at: datetime | None = None
    updated_at: datetime | None = None

    def to_dict(self) -> dict:
        payload = asdict(self)
        payload["job_id"] = str(self.job_id)
        payload["tenant_id"] = str(self.tenant_id)
        payload["user_id"] = str(self.user_id)
        for key in ("started_at", "completed_at", "updated_at"):
            value = payload.get(key)
            if isinstance(value, datetime):
                payload[key] = value.isoformat()
        payload["errors"] = [asdict(error) for error in self.errors]
        return payload

    @classmethod
    def from_dict(cls, payload: dict) -> BulkImportJobRecord:
        errors = [
            BulkImportJobError(**error) if isinstance(error, dict) else error
            for error in payload.get("errors", [])
        ]
        return cls(
            job_id=UUID(str(payload["job_id"])),
            type=payload.get("type", "bulk_import"),
            status=payload["status"],
            total_items=int(payload["total_items"]),
            tenant_id=UUID(str(payload["tenant_id"])),
            user_id=UUID(str(payload["user_id"])),
            source_type=payload["source_type"],
            items_payload=list(payload.get("items_payload", [])),
            processed=int(payload.get("processed", 0)),
            created=int(payload.get("created", 0)),
            skipped=int(payload.get("skipped", 0)),
            failed=int(payload.get("failed", 0)),
            errors=errors,
            skip_duplicates=bool(payload.get("skip_duplicates", True)),
            auto_geocode=bool(payload.get("auto_geocode", True)),
            default_status=str(payload.get("default_status", "draft")),
            started_at=_parse_dt(payload.get("started_at")),
            completed_at=_parse_dt(payload.get("completed_at")),
            updated_at=_parse_dt(payload.get("updated_at")),
        )


class ImportJobStore(Protocol):
    async def create(self, record: BulkImportJobRecord) -> None: ...

    async def get(self, job_id: UUID) -> BulkImportJobRecord | None: ...

    async def save(self, record: BulkImportJobRecord) -> None: ...


class InMemoryImportJobStore:
    def __init__(self) -> None:
        self._jobs: dict[str, BulkImportJobRecord] = {}

    async def create(self, record: BulkImportJobRecord) -> None:
        self._jobs[str(record.job_id)] = record

    async def get(self, job_id: UUID) -> BulkImportJobRecord | None:
        return self._jobs.get(str(job_id))

    async def save(self, record: BulkImportJobRecord) -> None:
        self._jobs[str(record.job_id)] = record


class RedisImportJobStore:
    def __init__(self, *, ttl_seconds: int = JOB_TTL_SECONDS) -> None:
        self._ttl_seconds = ttl_seconds

    def _key(self, job_id: UUID) -> str:
        return f"import_job:{job_id}"

    async def create(self, record: BulkImportJobRecord) -> None:
        client = await get_redis_client()
        await client.set(self._key(record.job_id), json.dumps(record.to_dict()))

    async def get(self, job_id: UUID) -> BulkImportJobRecord | None:
        client = await get_redis_client()
        raw = await client.get(self._key(job_id))
        if not raw:
            return None
        return BulkImportJobRecord.from_dict(json.loads(raw))

    async def save(self, record: BulkImportJobRecord) -> None:
        client = await get_redis_client()
        ttl = self._ttl_seconds
        if record.completed_at is not None:
            ttl = self._ttl_seconds
        await client.set(self._key(record.job_id), json.dumps(record.to_dict()), ex=ttl)


_store: ImportJobStore | None = None


def get_import_job_store() -> ImportJobStore:
    global _store
    if _store is None:
        settings = get_settings()
        if settings.cache_backend == "memory":
            _store = InMemoryImportJobStore()
        else:
            _store = RedisImportJobStore()
    return _store


def reset_import_job_store() -> None:
    global _store
    _store = None


def _parse_dt(value: object) -> datetime | None:
    if value is None or value == "":
        return None
    if isinstance(value, datetime):
        return value
    return datetime.fromisoformat(str(value).replace("Z", "+00:00"))


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


def completed_ttl_deadline() -> datetime:
    return utcnow() + timedelta(seconds=JOB_TTL_SECONDS)
