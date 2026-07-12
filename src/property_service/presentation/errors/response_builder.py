from __future__ import annotations

from fastapi import Request


def build_error_payload(
    request: Request,
    *,
    code: str,
    message: str,
    details: list[dict] | None = None,
) -> dict:
    return {
        "error": {
            "code": code,
            "message": message,
            "details": details or [],
            "correlation_id": getattr(request.state, "correlation_id", None),
        }
    }
