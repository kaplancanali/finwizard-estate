from __future__ import annotations

from property_service.application.commands import (
    ChangePropertyStatusCommand,
    CreatePropertyCommand,
    DeletePropertyCommand,
    RegisterFromSourceCommand,
    RestorePropertyCommand,
    UpdatePropertyCommand,
)
from property_service.application.auth_context import AuthContext
from property_service.application.services.property_application_service import PropertyApplicationService
from property_service.domain.factories.property_factory import CreatePropertyData


class CreatePropertyHandler:
    def __init__(self, service: PropertyApplicationService) -> None:
        self._service = service

    async def handle(self, command: CreatePropertyCommand, auth: AuthContext):
        data = CreatePropertyData(
            tenant_id=command.data.tenant_id,
            created_by=command.data.created_by,
            title=command.data.title,
            property_type=command.data.property_type,
            property_category=command.data.property_category,
            source_type=command.data.source_type,
            description=command.data.description,
            source_reference=command.data.source_reference,
        )
        return await self._service.create_property(data, auth)


class UpdatePropertyHandler:
    def __init__(self, service: PropertyApplicationService) -> None:
        self._service = service

    async def handle(self, command: UpdatePropertyCommand, auth: AuthContext):
        return await self._service.update_property(
            command.property_id,
            auth,
            expected_version=command.data.expected_version,
            title=command.data.title,
            description=command.data.description,
        )


class DeletePropertyHandler:
    def __init__(self, service: PropertyApplicationService) -> None:
        self._service = service

    async def handle(self, command: DeletePropertyCommand, auth: AuthContext) -> None:
        await self._service.delete_property(command.property_id, auth)


class RestorePropertyHandler:
    def __init__(self, service: PropertyApplicationService) -> None:
        self._service = service

    async def handle(self, command: RestorePropertyCommand, auth: AuthContext):
        return await self._service.restore_property(command.property_id, auth)


class ChangePropertyStatusHandler:
    def __init__(self, service: PropertyApplicationService) -> None:
        self._service = service

    async def handle(self, command: ChangePropertyStatusCommand, auth: AuthContext):
        return await self._service.change_status(
            command.property_id,
            command.status,
            auth,
            expected_version=command.expected_version,
            reason=command.reason,
        )


class RegisterFromSourceHandler:
    def __init__(self, service: PropertyApplicationService) -> None:
        self._service = service

    async def handle(self, command: RegisterFromSourceCommand, auth: AuthContext):
        data = CreatePropertyData(
            tenant_id=command.data.tenant_id,
            created_by=command.data.created_by,
            title=command.data.title,
            property_type=command.data.property_type,
            property_category=command.data.property_category,
            source_type=command.data.source_type,
            description=command.data.description,
            source_reference=command.data.source_reference,
        )
        return await self._service.register_from_source(data, auth)
