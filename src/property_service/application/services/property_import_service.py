from __future__ import annotations

from dataclasses import dataclass, field
from uuid import UUID, uuid4

from property_service.application.auth_context import AuthContext
from property_service.application.services.property_application_service import PropertyApplicationService
from property_service.domain.entities.property_location import PropertyLocation
from property_service.domain.entities.property_pricing import PropertyPricing
from property_service.domain.enums.property_category import PropertyCategory
from property_service.domain.enums.property_status import PropertyStatus
from property_service.domain.enums.property_type import PropertyType
from property_service.domain.enums.source_type import SourceType
from property_service.domain.exceptions import ValidationError
from property_service.domain.factories.property_factory import CreatePropertyData
from property_service.domain.services.listing_validator import ListingValidator
from property_service.infrastructure.jobs.import_job_store import (
    MAX_BULK_IMPORT_ITEMS,
    BulkImportJobError,
    BulkImportJobRecord,
    ImportJobStore,
    get_import_job_store,
    utcnow,
)
from property_service.application.mappers.bulk_import_mapper import (
    items_payload_to_create_property_data,
    serialize_items_payload,
)
from property_service.infrastructure.listing.listing_adapter import ListingAdapter, StubListingAdapter


@dataclass
class ImportJob:
    job_id: UUID
    status: str
    total_items: int = 0
    processed_items: int = 0
    created: int = 0
    skipped: int = 0
    errors: list[str] = field(default_factory=list)

    @classmethod
    def from_record(cls, record: BulkImportJobRecord) -> ImportJob:
        return cls(
            job_id=record.job_id,
            status=record.status,
            total_items=record.total_items,
            processed_items=record.processed,
            created=record.created,
            skipped=record.skipped,
            errors=[error.message for error in record.errors],
        )


class PropertyImportService:
    """Bulk and external source import orchestration."""

    def __init__(
        self,
        app_service: PropertyApplicationService,
        uow_factory,
        listing_adapter: ListingAdapter | None = None,
        job_store: ImportJobStore | None = None,
    ) -> None:
        self._app_service = app_service
        self._uow_factory = uow_factory
        self._listing_adapter = listing_adapter or StubListingAdapter()
        self._job_store = job_store or get_import_job_store()

    async def import_from_listing_url(self, url: str, auth: AuthContext, *, title: str | None = None):
        validated_url = ListingValidator.validate_url(url)
        provider = ListingValidator.resolve_provider(validated_url)
        ListingValidator.assert_supported_provider(provider)
        listing = await self._listing_adapter.fetch_listing(validated_url)
        async with self._uow_factory() as uow:
            if await uow.properties.exists_by_listing(listing.provider, listing.listing_id):
                raise ValidationError("Listing already imported", code="DUPLICATE_LISTING")

        data = CreatePropertyData(
            tenant_id=auth.tenant_id,
            created_by=auth.user_id,
            title=title or listing.title,
            description=listing.description,
            property_type=PropertyType.APARTMENT,
            property_category=PropertyCategory.RESIDENTIAL,
            location=PropertyLocation(
                country_code="TR",
                province=listing.province,
                district=listing.district,
            ),
            pricing=PropertyPricing(sale_price=listing.sale_price, currency=listing.currency),
            source_type=SourceType.LISTING_URL,
            source_reference=validated_url,
            source_payload=listing.raw_payload,
        )
        return await self._app_service.register_from_source(data, auth)

    async def bulk_import(
        self,
        *,
        items_payload: list[dict],
        source_type: SourceType,
        auth: AuthContext,
        async_mode: bool = True,
        skip_duplicates: bool = True,
        auto_geocode: bool = True,
        default_status: PropertyStatus = PropertyStatus.DRAFT,
    ) -> ImportJob:
        if len(items_payload) > MAX_BULK_IMPORT_ITEMS:
            raise ValidationError(
                f"Bulk import exceeds maximum of {MAX_BULK_IMPORT_ITEMS} items",
                code="BULK_IMPORT_TOO_LARGE",
            )

        job_id = uuid4()
        now = utcnow()
        record = BulkImportJobRecord(
            job_id=job_id,
            type="bulk_import",
            status="queued",
            total_items=len(items_payload),
            tenant_id=auth.tenant_id,
            user_id=auth.user_id,
            source_type=source_type.value,
            items_payload=serialize_items_payload(items_payload),
            skip_duplicates=skip_duplicates,
            auto_geocode=auto_geocode,
            default_status=default_status.value,
            started_at=now,
            updated_at=now,
        )
        await self._job_store.create(record)

        if async_mode:
            from property_service.infrastructure.celery.tasks.import_tasks import bulk_import as bulk_import_task

            bulk_import_task.delay(str(job_id))
            return ImportJob.from_record(record)

        await self._execute_bulk_import(record, auth)
        updated = await self._job_store.get(job_id)
        return ImportJob.from_record(updated or record)

    async def process_bulk_import_job(self, job_id: UUID) -> str:
        record = await self._job_store.get(job_id)
        if record is None:
            return "not_found"

        auth = AuthContext(tenant_id=record.tenant_id, user_id=record.user_id)
        await self._execute_bulk_import(record, auth)
        return f"completed:{job_id}"

    async def _execute_bulk_import(self, record: BulkImportJobRecord, auth: AuthContext) -> None:
        record.status = "processing"
        record.updated_at = utcnow()
        await self._job_store.save(record)

        source_type = SourceType(record.source_type)
        items = items_payload_to_create_property_data(
            record.items_payload,
            tenant_id=auth.tenant_id,
            user_id=auth.user_id,
            source_type=source_type,
        )

        for index, item in enumerate(items):
            try:
                if record.default_status:
                    item.status = PropertyStatus(record.default_status)
                await self._app_service.register_from_source(item, auth)
                record.created += 1
            except ValidationError as exc:
                if record.skip_duplicates and exc.code == "DUPLICATE_LISTING":
                    record.skipped += 1
                else:
                    record.failed += 1
                    record.errors.append(
                        BulkImportJobError(
                            index=index,
                            message=str(exc),
                            source_reference=item.source_reference,
                            code=exc.code,
                        )
                    )
            except Exception as exc:
                record.failed += 1
                record.errors.append(
                    BulkImportJobError(
                        index=index,
                        message=str(exc),
                        source_reference=item.source_reference,
                    )
                )
            finally:
                record.processed += 1
                record.updated_at = utcnow()
                await self._job_store.save(record)

        record.status = "completed" if record.failed == 0 else "completed_with_errors"
        record.completed_at = utcnow()
        record.updated_at = record.completed_at
        await self._job_store.save(record)

    async def get_job(self, job_id: UUID) -> ImportJob | None:
        record = await self._job_store.get(job_id)
        return ImportJob.from_record(record) if record else None

    async def sync_listing(self, property_id: UUID, auth: AuthContext) -> str:
        prop = await self._app_service.get_property(property_id, auth)
        source = prop.external_sources[0] if prop.external_sources else None
        if source is None or source.source_type != SourceType.LISTING_URL:
            raise ValidationError("Property has no listing URL to sync", code="LISTING_SOURCE_MISSING")

        from property_service.infrastructure.celery.tasks.sync_tasks import sync_listing_single

        sync_listing_single.delay(str(property_id))
        return "queued"

    async def sync_listing_inline(self, property_id: UUID, auth: AuthContext) -> str:
        prop = await self._app_service.get_property(property_id, auth)
        source = prop.external_sources[0] if prop.external_sources else None
        if source is None or source.source_type != SourceType.LISTING_URL:
            raise ValidationError("Property has no listing URL to sync", code="LISTING_SOURCE_MISSING")
        if not source.source_reference:
            raise ValidationError("Listing source reference missing", code="LISTING_SOURCE_MISSING")

        listing = await self._listing_adapter.fetch_listing(source.source_reference)
        return f"synced:{property_id}:{listing.listing_id}"
