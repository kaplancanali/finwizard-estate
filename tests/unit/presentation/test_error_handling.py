from __future__ import annotations

import pytest
from fastapi import HTTPException

from property_service.domain.exceptions import (
    ApplicationError,
    AuthorizationError,
    BulkLimitExceededError,
    ConcurrencyConflictError,
    DomainError,
    InfrastructureError,
    PresentationError,
    PropertyNotFoundError,
    PropertyServiceError,
    RateLimitExceededError,
    StorageError,
    TenantMismatchError,
    ValidationError,
)
from property_service.presentation.errors.error_registry import http_status_for_code, is_client_error
from property_service.presentation.errors.error_logging import log_service_error
from uuid import uuid4


class TestErrorHierarchy:
    def test_domain_error_is_property_service_error(self) -> None:
        exc = PropertyNotFoundError(uuid4())
        assert isinstance(exc, DomainError)
        assert isinstance(exc, PropertyServiceError)

    def test_application_error_layer(self) -> None:
        exc = TenantMismatchError()
        assert isinstance(exc, ApplicationError)

    def test_presentation_error_layer(self) -> None:
        exc = AuthorizationError()
        assert isinstance(exc, PresentationError)
        assert exc.code == "FORBIDDEN"

    def test_infrastructure_error_layer(self) -> None:
        exc = StorageError()
        assert isinstance(exc, InfrastructureError)
        assert http_status_for_code(exc.code) == 502


class TestErrorRegistry:
    def test_concurrency_conflict_is_409(self) -> None:
        assert http_status_for_code("CONCURRENCY_CONFLICT") == 409

    def test_tenant_mismatch_is_403(self) -> None:
        assert http_status_for_code("TENANT_MISMATCH") == 403

    def test_rate_limit_is_429(self) -> None:
        assert http_status_for_code("RATE_LIMIT_EXCEEDED") == 429

    def test_validation_input_is_400(self) -> None:
        assert http_status_for_code("VALIDATION_ERROR") == 400

    def test_domain_area_invalid_is_422(self) -> None:
        assert http_status_for_code("AREA_INVALID") == 422

    def test_client_error_classification(self) -> None:
        assert is_client_error(404) is True
        assert is_client_error(500) is False


class TestApplicationErrors:
    def test_bulk_limit_exceeded(self) -> None:
        with pytest.raises(BulkLimitExceededError) as exc_info:
            raise BulkLimitExceededError(max_items=1000, actual=1001)
        assert exc_info.value.code == "BULK_LIMIT_EXCEEDED"

    def test_rate_limit_retry_after(self) -> None:
        exc = RateLimitExceededError(retry_after=30)
        assert exc.retry_after == 30


class TestErrorLogging:
    def test_log_service_error_client_warning(self, caplog) -> None:
        exc = ValidationError("bad field", code="AREA_INVALID", field="building.net_area_sqm")
        with caplog.at_level("WARNING"):
            log_service_error(exc, correlation_id="corr-1", property_id=str(uuid4()))
        assert any("bad field" in record.message for record in caplog.records)
