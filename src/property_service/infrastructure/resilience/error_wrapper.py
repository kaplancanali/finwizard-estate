from __future__ import annotations

from collections.abc import Awaitable, Callable
from typing import TypeVar

from property_service.domain.exceptions.infrastructure_errors import (
    CacheError,
    DatabaseError,
    GeocodingError,
    MessagingError,
    StorageError,
)

T = TypeVar("T")

_INFRA_MAP: dict[str, type[Exception]] = {
    "database": DatabaseError,
    "cache": CacheError,
    "messaging": MessagingError,
    "storage": StorageError,
    "geocoding": GeocodingError,
}


def wrap_infrastructure_error(kind: str, exc: Exception) -> Exception:
    error_cls = _INFRA_MAP.get(kind, DatabaseError)
    return error_cls(str(exc)) from exc


async def run_with_infrastructure_guard(
    kind: str,
    operation: Callable[[], Awaitable[T]],
) -> T:
    try:
        return await operation()
    except Exception as exc:
        if isinstance(exc, tuple(_INFRA_MAP.values())):
            raise
        raise wrap_infrastructure_error(kind, exc) from exc
