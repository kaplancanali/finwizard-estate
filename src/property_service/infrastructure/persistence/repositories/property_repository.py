from __future__ import annotations

from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from property_service.domain.aggregates.property import Property
from property_service.domain.entities.property_ownership import OwnershipHistoryEntry
from property_service.domain.entities.property_pricing import PriceHistoryEntry
from property_service.domain.entities.property_version import PropertyAuditLog, PropertyVersion, StatusHistoryEntry
from property_service.domain.enums.property_status import PropertyStatus
from property_service.domain.exceptions import ConcurrencyConflictError, PropertyNotFoundError
from property_service.domain.repositories import AuditLogEntry, IPropertyRepository
from property_service.infrastructure.persistence.mappers.property_mapper import PropertyMapper
from property_service.infrastructure.persistence.models import (
    PropertyAuditLogModel,
    PropertyModel,
    PropertyOwnershipHistoryModel,
    PropertyPriceHistoryModel,
    PropertyStatusHistoryModel,
)

_LOAD_OPTIONS = (
    selectinload(PropertyModel.address),
    selectinload(PropertyModel.building),
    selectinload(PropertyModel.features),
    selectinload(PropertyModel.parcel),
    selectinload(PropertyModel.metadata_row),
    selectinload(PropertyModel.listing),
    selectinload(PropertyModel.images),
    selectinload(PropertyModel.videos),
    selectinload(PropertyModel.documents),
    selectinload(PropertyModel.amenities),
    selectinload(PropertyModel.tags),
    selectinload(PropertyModel.ownership),
    selectinload(PropertyModel.ownership_history),
    selectinload(PropertyModel.external_sources),
    selectinload(PropertyModel.price_history),
    selectinload(PropertyModel.status_history),
    selectinload(PropertyModel.audit_logs),
    selectinload(PropertyModel.versions),
    selectinload(PropertyModel.property_type_ref),
)


class SqlAlchemyPropertyRepository(IPropertyRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_id(
        self,
        property_id: UUID,
        tenant_id: UUID,
        *,
        include_deleted: bool = False,
    ) -> Property | None:
        stmt = (
            select(PropertyModel)
            .where(PropertyModel.id == property_id, PropertyModel.tenant_id == tenant_id)
            .options(*_LOAD_OPTIONS)
        )
        if not include_deleted:
            stmt = stmt.where(PropertyModel.deleted_at.is_(None))
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        return PropertyMapper.to_domain(model) if model else None

    async def get_by_code(self, property_code: str, tenant_id: UUID) -> Property | None:
        stmt = (
            select(PropertyModel)
            .where(
                PropertyModel.property_code == property_code.upper(),
                PropertyModel.tenant_id == tenant_id,
                PropertyModel.deleted_at.is_(None),
            )
            .options(*_LOAD_OPTIONS)
        )
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        return PropertyMapper.to_domain(model) if model else None

    async def get_by_slug(self, slug: str, tenant_id: UUID) -> Property | None:
        stmt = (
            select(PropertyModel)
            .where(
                PropertyModel.slug == slug.lower(),
                PropertyModel.tenant_id == tenant_id,
                PropertyModel.deleted_at.is_(None),
            )
            .options(*_LOAD_OPTIONS)
        )
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        return PropertyMapper.to_domain(model) if model else None

    async def exists_by_listing(self, provider: str, listing_id: str) -> bool:
        from property_service.infrastructure.persistence.models import PropertyListingModel
        stmt = select(PropertyListingModel.id).where(
            PropertyListingModel.provider == provider,
            PropertyListingModel.listing_id == listing_id,
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none() is not None

    async def add(self, property: Property) -> Property:
        model = PropertyMapper.to_model(property)
        self._session.add(model)
        await self._session.flush()
        return property

    async def update(self, property: Property) -> Property:
        stmt = (
            select(PropertyModel)
            .where(
                PropertyModel.id == property.id,
                PropertyModel.tenant_id == property.tenant_id,
            )
            .options(*_LOAD_OPTIONS)
            .with_for_update()
        )
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        if model is None:
            raise PropertyNotFoundError(property.id)
        if model.version != property.version - 1:
            raise ConcurrencyConflictError(property.id, property.version - 1, model.version)
        PropertyMapper.apply_to_model(property, model)
        await self._session.flush()
        return property

    async def soft_delete(self, property_id: UUID, tenant_id: UUID) -> None:
        stmt = select(PropertyModel).where(
            PropertyModel.id == property_id,
            PropertyModel.tenant_id == tenant_id,
            PropertyModel.deleted_at.is_(None),
        )
        model = (await self._session.execute(stmt)).scalar_one_or_none()
        if model is None:
            raise PropertyNotFoundError(property_id)
        model.deleted_at = datetime.now(timezone.utc)
        await self._session.flush()

    async def restore(self, property_id: UUID, tenant_id: UUID) -> Property:
        stmt = (
            select(PropertyModel)
            .where(
                PropertyModel.id == property_id,
                PropertyModel.tenant_id == tenant_id,
                PropertyModel.deleted_at.isnot(None),
            )
            .options(*_LOAD_OPTIONS)
        )
        model = (await self._session.execute(stmt)).scalar_one_or_none()
        if model is None:
            raise PropertyNotFoundError(property_id)
        model.deleted_at = None
        model.status = PropertyStatus.DRAFT.value
        await self._session.flush()
        return PropertyMapper.to_domain(model)

    async def bulk_soft_delete(self, property_ids: list[UUID], tenant_id: UUID) -> int:
        if not property_ids:
            return 0
        now = datetime.now(timezone.utc)
        stmt = select(PropertyModel).where(
            PropertyModel.id.in_(property_ids),
            PropertyModel.tenant_id == tenant_id,
            PropertyModel.deleted_at.is_(None),
        )
        rows = (await self._session.execute(stmt)).scalars().all()
        for model in rows:
            model.deleted_at = now
        await self._session.flush()
        return len(rows)

    async def get_price_history(
        self,
        property_id: UUID,
        *,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[PriceHistoryEntry], int]:
        count_stmt = select(func.count()).select_from(PropertyPriceHistoryModel).where(
            PropertyPriceHistoryModel.property_id == property_id
        )
        total = (await self._session.execute(count_stmt)).scalar_one()
        stmt = (
            select(PropertyPriceHistoryModel)
            .where(PropertyPriceHistoryModel.property_id == property_id)
            .order_by(PropertyPriceHistoryModel.changed_at.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
        rows = (await self._session.execute(stmt)).scalars().all()
        items = [
            PriceHistoryEntry(
                id=r.id,
                price_type=r.price_type,
                old_amount=r.old_amount,
                new_amount=r.new_amount,
                currency=r.currency,
                changed_by=r.changed_by,
                change_reason=r.change_reason,
            )
            for r in rows
        ]
        return items, total

    async def get_status_history(
        self,
        property_id: UUID,
        *,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[StatusHistoryEntry], int]:
        count_stmt = select(func.count()).select_from(PropertyStatusHistoryModel).where(
            PropertyStatusHistoryModel.property_id == property_id
        )
        total = (await self._session.execute(count_stmt)).scalar_one()
        stmt = (
            select(PropertyStatusHistoryModel)
            .where(PropertyStatusHistoryModel.property_id == property_id)
            .order_by(PropertyStatusHistoryModel.changed_at.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
        rows = (await self._session.execute(stmt)).scalars().all()
        return [
            StatusHistoryEntry(
                id=r.id,
                old_status=r.old_status,
                new_status=r.new_status,
                changed_by=r.changed_by,
                reason=r.reason,
            )
            for r in rows
        ], total

    async def get_ownership_history(
        self,
        property_id: UUID,
        *,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[OwnershipHistoryEntry], int]:
        from property_service.domain.enums.owner_type import OwnerType

        count_stmt = select(func.count()).select_from(PropertyOwnershipHistoryModel).where(
            PropertyOwnershipHistoryModel.property_id == property_id
        )
        total = (await self._session.execute(count_stmt)).scalar_one()
        stmt = (
            select(PropertyOwnershipHistoryModel)
            .where(PropertyOwnershipHistoryModel.property_id == property_id)
            .order_by(PropertyOwnershipHistoryModel.created_at.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
        rows = (await self._session.execute(stmt)).scalars().all()
        return [
            OwnershipHistoryEntry(
                id=r.id,
                owner_type=OwnerType(r.owner_type),
                owner_name=r.owner_name,
                owner_external_id=r.owner_external_id,
                ownership_percentage=r.ownership_percentage,
                acquired_at=r.acquired_at,
                released_at=r.released_at,
                effective_from=r.effective_from,
                effective_to=r.effective_to,
            )
            for r in rows
        ], total

    async def get_audit_logs(
        self,
        property_id: UUID,
        tenant_id: UUID,
        *,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[PropertyAuditLog], int]:
        count_stmt = select(func.count()).select_from(PropertyAuditLogModel).where(
            PropertyAuditLogModel.property_id == property_id,
            PropertyAuditLogModel.tenant_id == tenant_id,
        )
        total = (await self._session.execute(count_stmt)).scalar_one()
        stmt = (
            select(PropertyAuditLogModel)
            .where(
                PropertyAuditLogModel.property_id == property_id,
                PropertyAuditLogModel.tenant_id == tenant_id,
            )
            .order_by(PropertyAuditLogModel.created_at.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
        rows = (await self._session.execute(stmt)).scalars().all()
        return [
            PropertyAuditLog(
                id=r.id,
                action=r.action,
                actor_id=r.actor_id,
                actor_type=r.actor_type,
                changes=r.changes,
                correlation_id=r.correlation_id,
            )
            for r in rows
        ], total

    async def append_audit_log(self, entry: AuditLogEntry) -> None:
        self._session.add(
            PropertyAuditLogModel(
                property_id=entry.property_id,
                tenant_id=entry.tenant_id,
                action=entry.action,
                actor_id=entry.actor_id,
                actor_type=entry.actor_type,
                changes=entry.changes,
                ip_address=entry.ip_address,
                user_agent=entry.user_agent,
                correlation_id=entry.correlation_id,
            )
        )
