from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True)
class ApiKeyRecord:
    key_id: str
    tenant_id: UUID
    permissions: frozenset[str]
    label: str = "integration"


# Development API keys — production validates via Identity Service / Redis cache.
DEV_API_KEYS: dict[str, ApiKeyRecord] = {}


def register_dev_api_key(record: ApiKeyRecord) -> None:
    DEV_API_KEYS[record.key_id] = record


def lookup_api_key(key: str) -> ApiKeyRecord | None:
    return DEV_API_KEYS.get(key)


# Default integration key for local development.
register_dev_api_key(
    ApiKeyRecord(
        key_id="pk_dev_integration",
        tenant_id=UUID("00000000-0000-0000-0000-000000000010"),
        permissions=frozenset({"property:read", "property:search"}),
        label="dev-integration",
    )
)
