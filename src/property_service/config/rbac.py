from __future__ import annotations

# RBAC role and permission definitions (docs/architecture/12-security-strategy.md).

ROLE_PLATFORM_ADMIN = "platform_admin"
ROLE_TENANT_ADMIN = "tenant_admin"
ROLE_PROPERTY_MANAGER = "property_manager"
ROLE_PROPERTY_VIEWER = "property_viewer"
ROLE_PARTNER_READONLY = "partner_readonly"
ROLE_API_INTEGRATION = "api_integration"

ALL_PERMISSIONS: frozenset[str] = frozenset({
    "property:create",
    "property:read",
    "property:update",
    "property:delete",
    "property:search",
    "property:bulk_import",
    "property:bulk_update",
    "property:bulk_delete",
    "property:manage_media",
    "property:verify_documents",
    "property:manage_ownership",
    "property:audit",
    "property:statistics",
    "property:partner_read",
})

ROLE_PERMISSIONS: dict[str, frozenset[str]] = {
    ROLE_PLATFORM_ADMIN: ALL_PERMISSIONS,
    ROLE_TENANT_ADMIN: ALL_PERMISSIONS,
    ROLE_PROPERTY_MANAGER: frozenset({
        "property:create",
        "property:read",
        "property:update",
        "property:delete",
        "property:search",
        "property:bulk_import",
        "property:manage_media",
        "property:verify_documents",
        "property:manage_ownership",
        "property:statistics",
    }),
    ROLE_PROPERTY_VIEWER: frozenset({
        "property:read",
        "property:search",
        "property:statistics",
    }),
    ROLE_PARTNER_READONLY: frozenset({
        "property:partner_read",
        "property:search",
    }),
    ROLE_API_INTEGRATION: frozenset({
        "property:read",
        "property:search",
    }),
}

DEV_DEFAULT_ROLES: frozenset[str] = frozenset({ROLE_PROPERTY_MANAGER})


def permissions_for_roles(roles: frozenset[str]) -> frozenset[str]:
    merged: set[str] = set()
    for role in roles:
        merged.update(ROLE_PERMISSIONS.get(role, frozenset()))
    return frozenset(merged)
