from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class ErrorDetail:
    field: str | None = None
    message: str = ""
    code: str | None = None


@dataclass
class PropertyServiceError(Exception):
    message: str
    code: str
    details: list[ErrorDetail] = field(default_factory=list)

    def __str__(self) -> str:
        return self.message


class DomainError(PropertyServiceError):
    """Domain-layer business rule violations."""


class ApplicationError(PropertyServiceError):
    """Application orchestration and policy errors."""


class InfrastructureError(PropertyServiceError):
    """Infrastructure dependency failures."""


class PresentationError(PropertyServiceError):
    """HTTP/auth/presentation boundary errors."""
