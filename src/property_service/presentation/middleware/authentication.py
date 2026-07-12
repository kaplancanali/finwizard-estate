from __future__ import annotations

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from property_service.application.security.authenticator import authenticate_request


class AuthenticationMiddleware(BaseHTTPMiddleware):
    """Resolve AuthContext early for rate limiting and downstream dependencies."""

    async def dispatch(self, request: Request, call_next) -> Response:
        if request.url.path.startswith("/health") or request.url.path == "/metrics":
            return await call_next(request)

        request.state.auth = authenticate_request(request)
        return await call_next(request)
