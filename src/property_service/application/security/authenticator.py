from __future__ import annotations

from uuid import UUID, uuid4

from starlette.requests import Request

from property_service.application.auth_context import AuthContext
from property_service.application.security.api_keys import lookup_api_key
from property_service.application.security.jwt_validator import JwtValidator
from property_service.config import get_settings
from property_service.config.rbac import DEV_DEFAULT_ROLES, ROLE_PLATFORM_ADMIN, permissions_for_roles
from property_service.domain.exceptions import AuthenticationError, AuthorizationError, ValidationError

_DEV_USER_ID = UUID("00000000-0000-0000-0000-000000000001")
_DEV_TENANT_ID = UUID("00000000-0000-0000-0000-000000000010")
_jwt_validator = JwtValidator()


def _client_ip(request: Request) -> str | None:
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else None


def _parse_roles(payload: dict) -> frozenset[str]:
    raw = payload.get("roles") or []
    if isinstance(raw, str):
        return frozenset({raw})
    return frozenset(str(role) for role in raw)


def _parse_permissions(payload: dict, roles: frozenset[str]) -> frozenset[str]:
    raw = payload.get("permissions")
    if raw:
        if isinstance(raw, str):
            return frozenset({raw})
        return frozenset(str(p) for p in raw)
    return permissions_for_roles(roles)


def authenticate_request(request: Request) -> AuthContext:
    settings = get_settings()
    correlation_id = _correlation_id(request)
    ip_address = _client_ip(request)
    user_agent = request.headers.get("User-Agent")

    api_key = request.headers.get("X-API-Key")
    if api_key:
        return _auth_from_api_key(api_key, request, correlation_id, ip_address, user_agent)

    authorization = request.headers.get("Authorization")
    if authorization and authorization.startswith("Bearer "):
        return _auth_from_bearer(authorization[7:], request, correlation_id, ip_address, user_agent)

    if settings.is_development:
        roles = DEV_DEFAULT_ROLES
        return AuthContext(
            user_id=_DEV_USER_ID,
            tenant_id=_resolve_tenant_id(request, roles, _DEV_TENANT_ID),
            correlation_id=correlation_id,
            roles=roles,
            permissions=permissions_for_roles(roles),
            actor_type="user",
            client_id=f"user:{_DEV_USER_ID}",
            ip_address=ip_address,
            user_agent=user_agent,
        )

    if settings.require_authentication:
        raise AuthenticationError("Authentication required")

    roles = DEV_DEFAULT_ROLES
    return AuthContext(
        user_id=_DEV_USER_ID,
        tenant_id=_resolve_tenant_id(request, roles, _DEV_TENANT_ID),
        correlation_id=correlation_id,
        roles=roles,
        permissions=permissions_for_roles(roles),
        actor_type="user",
        client_id=f"user:{_DEV_USER_ID}",
        ip_address=ip_address,
        user_agent=user_agent,
    )


def _auth_from_bearer(
    token: str,
    request: Request,
    correlation_id: UUID | None,
    ip_address: str | None,
    user_agent: str | None,
) -> AuthContext:
    settings = get_settings()
    payload = _jwt_validator.safe_decode(token)
    if payload is None:
        if settings.is_development:
            return AuthContext(
                user_id=_DEV_USER_ID,
                tenant_id=_DEV_TENANT_ID,
                correlation_id=correlation_id,
                roles=DEV_DEFAULT_ROLES,
                permissions=permissions_for_roles(DEV_DEFAULT_ROLES),
                client_id=f"user:{_DEV_USER_ID}",
                ip_address=ip_address,
                user_agent=user_agent,
            )
        raise AuthenticationError("Invalid token")

    roles = _parse_roles(payload)
    permissions = _parse_permissions(payload, roles)
    user_id = _jwt_validator.parse_uuid(payload.get("sub"), field="sub")
    tenant_id = _jwt_validator.parse_uuid(payload.get("tenant_id", _DEV_TENANT_ID), field="tenant_id")
    tenant_id = _resolve_tenant_id(request, roles, tenant_id)

    return AuthContext(
        user_id=user_id,
        tenant_id=tenant_id,
        correlation_id=correlation_id,
        roles=roles,
        permissions=permissions,
        actor_type="user",
        client_id=f"user:{user_id}",
        ip_address=ip_address,
        user_agent=user_agent,
    )


def _auth_from_api_key(
    api_key: str,
    request: Request,
    correlation_id: UUID | None,
    ip_address: str | None,
    user_agent: str | None,
) -> AuthContext:
    record = lookup_api_key(api_key)
    if record is None:
        raise AuthenticationError("Invalid API key")

    return AuthContext(
        user_id=UUID(int=0),
        tenant_id=record.tenant_id,
        correlation_id=correlation_id,
        roles=frozenset({"api_integration"}),
        permissions=record.permissions,
        actor_type="api_key",
        client_id=f"apikey:{record.key_id}",
        ip_address=ip_address,
        user_agent=user_agent,
    )


def _resolve_tenant_id(request: Request, roles: frozenset[str], token_tenant_id: UUID) -> UUID:
    header_tenant = request.headers.get("X-Tenant-ID")
    if not header_tenant:
        return token_tenant_id
    try:
        override = UUID(header_tenant)
    except ValueError:
        raise ValidationError("Invalid X-Tenant-ID", code="VALIDATION_ERROR", field="X-Tenant-ID") from None
    if ROLE_PLATFORM_ADMIN in roles:
        return override
    raise AuthorizationError("X-Tenant-ID override requires platform_admin role")


def _correlation_id(request: Request) -> UUID | None:
    raw = getattr(request.state, "correlation_id", None)
    if raw is None:
        return None
    try:
        return UUID(str(raw))
    except ValueError:
        return uuid4()
