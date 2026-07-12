from __future__ import annotations

from property_service.domain.exceptions.base import InfrastructureError


class DatabaseError(InfrastructureError):
    def __init__(self, message: str = "Database operation failed") -> None:
        super().__init__(message=message, code="INTERNAL_ERROR")


class CacheError(InfrastructureError):
    def __init__(self, message: str = "Cache operation failed") -> None:
        super().__init__(message=message, code="INTERNAL_ERROR")


class MessagingError(InfrastructureError):
    def __init__(self, message: str = "Messaging operation failed") -> None:
        super().__init__(message=message, code="SERVICE_UNAVAILABLE")


class StorageError(InfrastructureError):
    def __init__(self, message: str = "Object storage operation failed") -> None:
        super().__init__(message=message, code="STORAGE_ERROR")


class GeocodingError(InfrastructureError):
    def __init__(self, message: str = "Geocoding service failed") -> None:
        super().__init__(message=message, code="GEOCODING_FAILED")
