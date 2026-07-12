from __future__ import annotations

from uuid import UUID

from property_service.application.auth_context import AuthContext
from property_service.config.rbac import (
    ROLE_PLATFORM_ADMIN,
    ROLE_PROPERTY_MANAGER,
    ROLE_TENANT_ADMIN,
)
from property_service.domain.aggregates.property import Property
from property_service.domain.exceptions import AuthorizationError


class OwnershipGuard:
    """B2C ownership checks for property mutations."""

    @staticmethod
    def can_modify_property(auth: AuthContext, prop: Property) -> bool:
        if "property:update" not in auth.permissions:
            return False
        if auth.tenant_id != prop.tenant_id:
            return False
        if auth.has_role(ROLE_PLATFORM_ADMIN) or auth.has_role(ROLE_TENANT_ADMIN):
            return True
        if auth.has_role(ROLE_PROPERTY_MANAGER):
            return True
        if prop.created_by == auth.user_id:
            return True
        return any(
            owner.is_current and owner.owner_external_id == auth.user_id
            for owner in prop.ownership
        )

    @staticmethod
    def assert_can_modify(auth: AuthContext, prop: Property) -> None:
        if not OwnershipGuard.can_modify_property(auth, prop):
            raise AuthorizationError("Not authorized to modify this property")
