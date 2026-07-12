from __future__ import annotations

from uuid import UUID

from property_service.application.auth_context import AuthContext
from property_service.domain.exceptions import PropertyNotFoundError


class PropertyHistoryService:
    """Read-only history and versioning — does not mutate property state."""

    def __init__(self, uow_factory) -> None:
        self._uow_factory = uow_factory

    async def _ensure_property(self, uow, property_id: UUID, tenant_id: UUID) -> None:
        prop = await uow.properties.get_by_id(property_id, tenant_id)
        if prop is None:
            raise PropertyNotFoundError(property_id)

    async def get_price_history(
        self, property_id: UUID, auth: AuthContext, *, page: int = 1, page_size: int = 20
    ):
        async with self._uow_factory() as uow:
            await self._ensure_property(uow, property_id, auth.tenant_id)
            return await uow.properties.get_price_history(property_id, page=page, page_size=page_size)

    async def get_status_history(
        self, property_id: UUID, auth: AuthContext, *, page: int = 1, page_size: int = 20
    ):
        async with self._uow_factory() as uow:
            await self._ensure_property(uow, property_id, auth.tenant_id)
            return await uow.properties.get_status_history(property_id, page=page, page_size=page_size)

    async def get_ownership_history(
        self, property_id: UUID, auth: AuthContext, *, page: int = 1, page_size: int = 20
    ):
        async with self._uow_factory() as uow:
            await self._ensure_property(uow, property_id, auth.tenant_id)
            return await uow.properties.get_ownership_history(property_id, page=page, page_size=page_size)

    async def get_versions(
        self, property_id: UUID, auth: AuthContext, *, page: int = 1, page_size: int = 20
    ):
        async with self._uow_factory() as uow:
            await self._ensure_property(uow, property_id, auth.tenant_id)
            return await uow.versions.get_versions(property_id, page=page, page_size=page_size)

    async def get_version(self, property_id: UUID, version_number: int, auth: AuthContext):
        async with self._uow_factory() as uow:
            version = await uow.versions.get_version(property_id, version_number)
            if version is None:
                raise PropertyNotFoundError(property_id)
            return version

    async def get_audit_logs(
        self, property_id: UUID, auth: AuthContext, *, page: int = 1, page_size: int = 20
    ):
        async with self._uow_factory() as uow:
            return await uow.properties.get_audit_logs(
                property_id, auth.tenant_id, page=page, page_size=page_size
            )
