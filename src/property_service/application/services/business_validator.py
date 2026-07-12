from __future__ import annotations

from uuid import UUID

from property_service.application.auth_context import AuthContext
from property_service.domain.aggregates.property import Property
from property_service.domain.enums.property_visibility import PropertyVisibility
from property_service.domain.exceptions import (
    AuthorizationError,
    BulkLimitExceededError,
    TenantMismatchError,
)


class BusinessValidator:
    """Application-layer authorization and cross-cutting business rules."""

    @staticmethod
    def require_permission(auth: AuthContext, permission: str) -> None:
        if permission not in auth.permissions:
            raise AuthorizationError(f"Missing permission '{permission}'")

    @staticmethod
    def assert_tenant_scope(property_tenant_id: UUID, auth: AuthContext) -> None:
        if property_tenant_id != auth.tenant_id:
            raise TenantMismatchError()

    @staticmethod
    def assert_bulk_limit(item_count: int, *, max_items: int = 1000) -> None:
        if item_count > max_items:
            raise BulkLimitExceededError(max_items=max_items, actual=item_count)

    @staticmethod
    def assert_property_readable(prop: Property, auth: AuthContext) -> None:
        if "property:read" in auth.permissions:
            return
        if "property:partner_read" in auth.permissions:
            if prop.visibility in (PropertyVisibility.PUBLIC, PropertyVisibility.PARTNER):
                return
            raise AuthorizationError(
                "Partner access limited to public or partner-visible properties",
            )
        raise AuthorizationError("Missing property read permission")
