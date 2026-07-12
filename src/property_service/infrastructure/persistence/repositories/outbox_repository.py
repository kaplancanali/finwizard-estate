from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from property_service.domain.entities.property_version import PropertyVersion
from property_service.domain.events.base import DomainEvent
from property_service.domain.events.catalog import MAX_OUTBOX_RETRIES
from property_service.domain.repositories import IOutboxRepository, IPropertyVersionRepository, OutboxEvent
from property_service.infrastructure.persistence.models import OutboxEventModel, PropertyVersionModel


class SqlAlchemyOutboxRepository(IOutboxRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def add_events(self, events: list[DomainEvent]) -> None:
        for event in events:
            actor_id = None
            for field in ("updated_by", "created_by", "deleted_by", "changed_by", "restored_by"):
                value = getattr(event, field, None)
                if value is not None:
                    actor_id = str(value)
                    break

            self._session.add(
                OutboxEventModel(
                    id=event.event_id,
                    aggregate_id=event.aggregate_id or UUID(int=0),
                    event_type=event.cloud_events_type,
                    payload=event.to_payload(),
                    metadata_json={
                        "tenant_id": str(event.tenant_id) if event.tenant_id else None,
                        "correlation_id": str(event.correlation_id) if event.correlation_id else None,
                        "actor_id": actor_id,
                        "routing_key": event.routing_key,
                        "event_version": event.event_version,
                        "occurred_at": event.occurred_at.isoformat(),
                    },
                )
            )

    async def get_pending(self, *, batch_size: int = 100) -> list[OutboxEvent]:
        from property_service.config import get_settings

        stmt = (
            select(OutboxEventModel)
            .where(OutboxEventModel.status == "pending")
            .order_by(OutboxEventModel.created_at)
            .limit(batch_size)
        )
        if "sqlite" not in get_settings().database_url:
            stmt = stmt.with_for_update(skip_locked=True)
        rows = (await self._session.execute(stmt)).scalars().all()
        return [
            OutboxEvent(
                id=r.id,
                aggregate_id=r.aggregate_id,
                event_type=r.event_type,
                payload=r.payload,
                status=r.status,
                metadata=r.metadata_json or {},
                routing_key=(r.metadata_json or {}).get("routing_key"),
                retry_count=r.retry_count,
            )
            for r in rows
        ]

    async def mark_published(self, event_ids: list[UUID]) -> None:
        if not event_ids:
            return
        stmt = select(OutboxEventModel).where(OutboxEventModel.id.in_(event_ids))
        rows = (await self._session.execute(stmt)).scalars().all()
        from datetime import datetime, timezone
        for r in rows:
            r.status = "published"
            r.published_at = datetime.now(timezone.utc)

    async def mark_failed(self, event_id: UUID, *, increment_retry: bool = True) -> None:
        stmt = select(OutboxEventModel).where(OutboxEventModel.id == event_id)
        row = (await self._session.execute(stmt)).scalar_one_or_none()
        if row:
            if increment_retry:
                row.retry_count += 1
            if row.retry_count >= MAX_OUTBOX_RETRIES:
                row.status = "failed"


class SqlAlchemyVersionRepository(IPropertyVersionRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create_snapshot(
        self,
        property_id: UUID,
        version_number: int,
        snapshot: dict,
        change_summary: str,
        created_by: UUID,
    ) -> PropertyVersion:
        model = PropertyVersionModel(
            property_id=property_id,
            version_number=version_number,
            snapshot=snapshot,
            change_summary=change_summary,
            created_by=created_by,
        )
        self._session.add(model)
        await self._session.flush()
        return PropertyVersion(
            id=model.id,
            version_number=version_number,
            snapshot=snapshot,
            change_summary=change_summary,
            created_by=created_by,
        )

    async def get_versions(
        self,
        property_id: UUID,
        *,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[PropertyVersion], int]:
        from sqlalchemy import func
        total = (
            await self._session.execute(
                select(func.count()).select_from(PropertyVersionModel).where(
                    PropertyVersionModel.property_id == property_id
                )
            )
        ).scalar_one()
        stmt = (
            select(PropertyVersionModel)
            .where(PropertyVersionModel.property_id == property_id)
            .order_by(PropertyVersionModel.version_number.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
        rows = (await self._session.execute(stmt)).scalars().all()
        return [
            PropertyVersion(
                id=r.id,
                version_number=r.version_number,
                snapshot=r.snapshot,
                change_summary=r.change_summary,
                created_by=r.created_by,
            )
            for r in rows
        ], total

    async def get_version(self, property_id: UUID, version_number: int) -> PropertyVersion | None:
        stmt = select(PropertyVersionModel).where(
            PropertyVersionModel.property_id == property_id,
            PropertyVersionModel.version_number == version_number,
        )
        r = (await self._session.execute(stmt)).scalar_one_or_none()
        if not r:
            return None
        return PropertyVersion(
            id=r.id,
            version_number=r.version_number,
            snapshot=r.snapshot,
            change_summary=r.change_summary,
            created_by=r.created_by,
        )

    async def get_latest_version_number(self, property_id: UUID) -> int:
        from sqlalchemy import func
        stmt = select(func.max(PropertyVersionModel.version_number)).where(
            PropertyVersionModel.property_id == property_id
        )
        result = (await self._session.execute(stmt)).scalar_one_or_none()
        return result or 0
