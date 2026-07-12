from __future__ import annotations

from uuid import UUID, uuid4

from property_service.application.auth_context import AuthContext
from property_service.application.services.business_validator import BusinessValidator
from property_service.application.services.event_persistence import persist_domain_events
from property_service.application.security.ownership import OwnershipGuard
from property_service.application.services.metadata_validator import MetadataSchemaValidator
from property_service.domain.aggregates.property import Property
from property_service.domain.entities.property_building import PropertyBuilding
from property_service.domain.entities.property_features import PropertyFeatures
from property_service.domain.entities.property_image import PropertyAmenity
from property_service.domain.entities.property_location import PropertyLocation
from property_service.domain.entities.property_pricing import PropertyPricing
from property_service.domain.enums.property_status import PropertyStatus
from property_service.domain.enums.source_type import SourceType
from property_service.domain.exceptions import PropertyNotFoundError
from property_service.domain.factories.property_factory import CreatePropertyData, PropertyFactory
from property_service.infrastructure.cache.property_cache_manager import PropertyCacheManager

__all__ = ["AuthContext", "PropertyApplicationService"]


class PropertyApplicationService:
    def __init__(
        self,
        uow_factory,
        factory: PropertyFactory | None = None,
        cache_manager: PropertyCacheManager | None = None,
    ) -> None:
        self._uow_factory = uow_factory
        self._factory = factory or PropertyFactory()
        self._cache = cache_manager
        self._metadata_validator = MetadataSchemaValidator()

    async def create_property(self, data: CreatePropertyData, auth: AuthContext) -> Property:
        BusinessValidator.require_permission(auth, "property:create")
        data.tenant_id = auth.tenant_id
        data.created_by = auth.user_id
        prop = self._factory.create_from_manual(data)
        async with self._uow_factory() as uow:
            await uow.properties.add(prop)
            await persist_domain_events(uow, prop, auth, cache_manager=self._cache)
        return prop

    async def register_from_source(self, data: CreatePropertyData, auth: AuthContext) -> Property:
        data.tenant_id = auth.tenant_id
        data.created_by = auth.user_id
        if data.source_type == SourceType.COORDINATES:
            prop = self._factory.create_from_coordinates(data)
        elif data.source_type == SourceType.ADDRESS:
            prop = self._factory.create_from_address(data)
        elif data.source_type == SourceType.LISTING_URL:
            prop = self._factory.create_from_listing_url(data, data.source_reference or "")
        elif data.source_type == SourceType.PARCEL:
            prop = self._factory.create_from_parcel(data)
        else:
            prop = self._factory.create_from_manual(data)
        async with self._uow_factory() as uow:
            await uow.properties.add(prop)
            await persist_domain_events(uow, prop, auth, cache_manager=self._cache)
        return prop

    register_property = register_from_source

    async def get_property(self, property_id: UUID, auth: AuthContext) -> Property:
        async with self._uow_factory() as uow:
            prop = await uow.properties.get_by_id(property_id, auth.tenant_id)
            if prop is None:
                raise PropertyNotFoundError(property_id)
            BusinessValidator.assert_property_readable(prop, auth)
            return prop

    async def get_by_code(self, code: str, auth: AuthContext) -> Property:
        if self._cache:
            cached_id = await self._cache.get_property_id_by_code(auth.tenant_id, code)
            if cached_id:
                return await self.get_property(UUID(cached_id), auth)
        async with self._uow_factory() as uow:
            prop = await uow.properties.get_by_code(code, auth.tenant_id)
            if prop is None:
                raise PropertyNotFoundError(uuid4())
            if self._cache:
                await self._cache.set_property_id_by_code(auth.tenant_id, code, prop.id)
            BusinessValidator.assert_property_readable(prop, auth)
            return prop

    async def get_by_slug(self, slug: str, auth: AuthContext) -> Property:
        if self._cache:
            cached_id = await self._cache.get_property_id_by_slug(auth.tenant_id, slug)
            if cached_id:
                return await self.get_property(UUID(cached_id), auth)
        async with self._uow_factory() as uow:
            prop = await uow.properties.get_by_slug(slug, auth.tenant_id)
            if prop is None:
                raise PropertyNotFoundError(uuid4())
            if self._cache:
                await self._cache.set_property_id_by_slug(auth.tenant_id, slug, prop.id)
            BusinessValidator.assert_property_readable(prop, auth)
            return prop

    async def update_property(
        self,
        property_id: UUID,
        auth: AuthContext,
        *,
        expected_version: int,
        title: str | None = None,
        description: str | None = None,
        pricing: PropertyPricing | None = None,
        location: PropertyLocation | None = None,
        building: PropertyBuilding | None = None,
        features: PropertyFeatures | None = None,
        amenities: list[str] | None = None,
        tags: list[str] | None = None,
    ) -> Property:
        BusinessValidator.require_permission(auth, "property:update")
        async with self._uow_factory() as uow:
            prop = await uow.properties.get_by_id(property_id, auth.tenant_id)
            if prop is None:
                raise PropertyNotFoundError(property_id)
            prop.assert_version(expected_version)
            OwnershipGuard.assert_can_modify(auth, prop)

            if title is not None:
                prop.update_title(title, auth.user_id)
            if description is not None:
                prop.update_description(description, auth.user_id)
            if pricing is not None:
                prop.update_pricing(pricing, auth.user_id)
            if location is not None:
                prop.update_location(location, auth.user_id)
            if building is not None:
                from property_service.domain.services.property_validator import PropertyValidator

                PropertyValidator.validate_building(building, prop.classification.property_type)
                prop.building = building
                prop.building.compute_building_age()
                prop.pricing.compute_price_per_sqm(prop.building.net_area_sqm)
                prop._touch(auth.user_id)  # noqa: SLF001
            if features is not None:
                prop.features = features
                prop._touch(auth.user_id)  # noqa: SLF001
            if amenities is not None:
                prop.set_amenities([PropertyAmenity(amenity_code=a) for a in amenities], auth.user_id)
            if tags is not None:
                prop.set_tags(tags, auth.user_id)

            await uow.properties.update(prop)
            await persist_domain_events(uow, prop, auth, cache_manager=self._cache)
            return prop

    async def change_status(
        self,
        property_id: UUID,
        new_status: PropertyStatus,
        auth: AuthContext,
        *,
        expected_version: int,
        reason: str | None = None,
    ) -> Property:
        BusinessValidator.require_permission(auth, "property:update")
        async with self._uow_factory() as uow:
            prop = await uow.properties.get_by_id(property_id, auth.tenant_id)
            if prop is None:
                raise PropertyNotFoundError(property_id)
            prop.assert_version(expected_version)
            prop.change_status(new_status, auth.user_id, reason=reason)
            await uow.properties.update(prop)
            await persist_domain_events(uow, prop, auth, cache_manager=self._cache)
            return prop

    async def delete_property(self, property_id: UUID, auth: AuthContext) -> None:
        BusinessValidator.require_permission(auth, "property:delete")
        async with self._uow_factory() as uow:
            prop = await uow.properties.get_by_id(property_id, auth.tenant_id)
            if prop is None:
                raise PropertyNotFoundError(property_id)
            OwnershipGuard.assert_can_modify(auth, prop)
            prop.soft_delete(auth.user_id)
            await uow.properties.update(prop)
            await persist_domain_events(uow, prop, auth, cache_manager=self._cache)

    async def restore_property(self, property_id: UUID, auth: AuthContext) -> Property:
        async with self._uow_factory() as uow:
            prop = await uow.properties.get_by_id(property_id, auth.tenant_id, include_deleted=True)
            if prop is None:
                raise PropertyNotFoundError(property_id)
            prop.restore(auth.user_id)
            await uow.properties.update(prop)
            await persist_domain_events(uow, prop, auth, cache_manager=self._cache)
            return prop

    async def get_metadata(self, property_id: UUID, auth: AuthContext):
        prop = await self.get_property(property_id, auth)
        return prop.metadata

    async def update_metadata(
        self,
        property_id: UUID,
        auth: AuthContext,
        *,
        metadata: dict | None = None,
        tenant_extensions: dict | None = None,
    ) -> Property:
        BusinessValidator.require_permission(auth, "property:update")
        async with self._uow_factory() as uow:
            prop = await uow.properties.get_by_id(property_id, auth.tenant_id)
            if prop is None:
                raise PropertyNotFoundError(property_id)
            if metadata is not None:
                self._metadata_validator.validate(prop.classification.property_type.value, metadata)
                prop.metadata.metadata = metadata
            if tenant_extensions is not None:
                prop.metadata.tenant_extensions = tenant_extensions
            prop._touch(auth.user_id)  # noqa: SLF001
            await uow.properties.update(prop)
            await persist_domain_events(uow, prop, auth, cache_manager=self._cache)
            return prop

    async def bulk_delete(self, property_ids: list[UUID], auth: AuthContext) -> int:
        BusinessValidator.require_permission(auth, "property:delete")
        BusinessValidator.assert_bulk_limit(len(property_ids), max_items=1000)
        deleted = 0
        for property_id in property_ids:
            await self.delete_property(property_id, auth)
            deleted += 1
        return deleted
