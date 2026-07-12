from __future__ import annotations

from typing import Any
from uuid import UUID, uuid4

from property_service.config import get_settings
from property_service.application.auth_context import AuthContext
from property_service.application.services.event_persistence import persist_domain_events
from property_service.domain.entities.property_document import PropertyDocument
from property_service.domain.entities.property_image import PropertyImage
from property_service.domain.enums.document_type import DocumentType
from property_service.domain.exceptions import PropertyNotFoundError, ValidationError
from property_service.infrastructure.cache.property_cache_manager import PropertyCacheManager
from property_service.application.ports.object_storage import IObjectStorage


class PropertyMediaService:
    """Media upload lifecycle — presigned URLs, confirmation, reorder, delete."""

    def __init__(
        self,
        uow_factory,
        storage: IObjectStorage,
        cache_manager: PropertyCacheManager | None = None,
    ) -> None:
        self._uow_factory = uow_factory
        self._storage = storage
        self._cache = cache_manager

    def _image_key(self, tenant_id: UUID, property_id: UUID, image_id: UUID, file_name: str) -> str:
        ext = file_name.rsplit(".", 1)[-1] if "." in file_name else "jpg"
        return f"{tenant_id}/properties/{property_id}/images/{image_id}.{ext}"

    def _document_key(self, tenant_id: UUID, property_id: UUID, document_id: UUID, file_name: str) -> str:
        ext = file_name.rsplit(".", 1)[-1] if "." in file_name else "pdf"
        return f"{tenant_id}/properties/{property_id}/documents/{document_id}.{ext}"

    async def initiate_image_upload(
        self,
        property_id: UUID,
        auth: AuthContext,
        *,
        file_name: str,
        mime_type: str | None = None,
        file_size: int | None = None,
        caption: str | None = None,
        is_primary: bool = False,
        sort_order: int = 0,
    ) -> dict[str, Any]:
        image_id = uuid4()
        storage_key = self._image_key(auth.tenant_id, property_id, image_id, file_name)
        mime = mime_type or "image/jpeg"
        ttl = get_settings().presigned_url_ttl_seconds
        upload_url = await self._storage.generate_upload_url(storage_key, mime, expires_in=ttl)
        image = PropertyImage(
            id=image_id,
            storage_key=storage_key,
            url=await self._storage.get_public_url(storage_key),
            caption=caption,
            is_primary=is_primary,
            sort_order=sort_order,
            mime_type=mime_type,
            file_size=file_size,
        )
        async with self._uow_factory() as uow:
            prop = await uow.properties.get_by_id(property_id, auth.tenant_id)
            if prop is None:
                raise PropertyNotFoundError(property_id)
            prop.add_image(image, auth.user_id)
            await uow.properties.update(prop)
            await persist_domain_events(uow, prop, auth, cache_manager=self._cache)
            version = prop.version
        return {
            "image": image,
            "upload_url": upload_url,
            "property_version": version,
        }

    async def confirm_image_upload(self, property_id: UUID, image_id: UUID, auth: AuthContext) -> dict[str, str]:
        async with self._uow_factory() as uow:
            prop = await uow.properties.get_by_id(property_id, auth.tenant_id)
            if prop is None:
                raise PropertyNotFoundError(property_id)
            image = next((i for i in prop.active_images if i.id == image_id), None)
            if image is None:
                raise ValidationError(f"Image {image_id} not found", code="IMAGE_NOT_FOUND")
            if not await self._storage.object_exists(image.storage_key):
                raise ValidationError("Uploaded object not found in storage", code="STORAGE_OBJECT_MISSING")
            storage_key = image.storage_key

        from property_service.infrastructure.celery.tasks import process_image_upload

        process_image_upload.delay(storage_key)
        return {"property_id": str(property_id), "image_id": str(image_id), "status": "processing"}

    async def reorder_images(self, property_id: UUID, image_ids: list[UUID], auth: AuthContext) -> int:
        async with self._uow_factory() as uow:
            prop = await uow.properties.get_by_id(property_id, auth.tenant_id)
            if prop is None:
                raise PropertyNotFoundError(property_id)
            prop.reorder_images(image_ids, auth.user_id)
            await uow.properties.update(prop)
            await persist_domain_events(uow, prop, auth, cache_manager=self._cache)
            return prop.version

    async def delete_image(self, property_id: UUID, image_id: UUID, auth: AuthContext) -> None:
        async with self._uow_factory() as uow:
            prop = await uow.properties.get_by_id(property_id, auth.tenant_id)
            if prop is None:
                raise PropertyNotFoundError(property_id)
            image = next((i for i in prop.active_images if i.id == image_id), None)
            storage_key = image.storage_key if image else None
            prop.remove_image(image_id, auth.user_id)
            await uow.properties.update(prop)
            await persist_domain_events(uow, prop, auth, cache_manager=self._cache)
        if storage_key:
            await self._storage.delete_object(storage_key)

    async def initiate_document_upload(
        self,
        property_id: UUID,
        auth: AuthContext,
        *,
        file_name: str,
        document_type: str,
        mime_type: str | None = None,
        file_size: int | None = None,
    ) -> dict[str, Any]:
        document_id = uuid4()
        storage_key = self._document_key(auth.tenant_id, property_id, document_id, file_name)
        mime = mime_type or "application/pdf"
        ttl = get_settings().presigned_url_ttl_seconds
        upload_url = await self._storage.generate_upload_url(storage_key, mime, expires_in=ttl)
        document = PropertyDocument(
            id=document_id,
            document_type=DocumentType(document_type),
            storage_key=storage_key,
            url=await self._storage.get_public_url(storage_key),
            file_name=file_name,
            mime_type=mime_type,
            file_size=file_size,
        )
        async with self._uow_factory() as uow:
            prop = await uow.properties.get_by_id(property_id, auth.tenant_id)
            if prop is None:
                raise PropertyNotFoundError(property_id)
            prop.add_document(document, auth.user_id)
            await uow.properties.update(prop)
            await persist_domain_events(uow, prop, auth, cache_manager=self._cache)
            version = prop.version
        return {"document": document, "upload_url": upload_url, "property_version": version}

    async def verify_document(self, property_id: UUID, document_id: UUID, auth: AuthContext) -> int:
        async with self._uow_factory() as uow:
            prop = await uow.properties.get_by_id(property_id, auth.tenant_id)
            if prop is None:
                raise PropertyNotFoundError(property_id)
            prop.verify_document(document_id, auth.user_id)
            await uow.properties.update(prop)
            await persist_domain_events(uow, prop, auth, cache_manager=self._cache)
            return prop.version
