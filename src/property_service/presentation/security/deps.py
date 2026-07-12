from __future__ import annotations

from fastapi import Depends

from property_service.application.auth_context import AuthContext
from property_service.application.security.authenticator import authenticate_request
from property_service.application.services.business_validator import BusinessValidator
from starlette.requests import Request


async def get_auth_context(request: Request) -> AuthContext:
    auth = getattr(request.state, "auth", None)
    if auth is None:
        auth = authenticate_request(request)
        request.state.auth = auth
    return auth


def require_permission(permission: str):
    async def dependency(auth: AuthContext = Depends(get_auth_context)) -> AuthContext:
        BusinessValidator.require_permission(auth, permission)
        return auth

    return dependency
