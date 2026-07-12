from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID


@dataclass
class AuthContext:
    user_id: UUID
    tenant_id: UUID
    correlation_id: UUID | None = None
    roles: frozenset[str] = frozenset()
    permissions: frozenset[str] = frozenset()
    actor_type: str = "user"
    client_id: str | None = None
    ip_address: str | None = None
    user_agent: str | None = None

    @property
    def primary_role(self) -> str | None:
        return next(iter(self.roles), None)

    def has_role(self, role: str) -> bool:
        return role in self.roles

    def is_platform_admin(self) -> bool:
        return self.has_role("platform_admin")
