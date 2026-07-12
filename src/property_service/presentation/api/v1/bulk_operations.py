from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, Request
from fastapi.responses import JSONResponse

from property_service.application.auth_context import AuthContext
from property_service.application.services.property_application_service import PropertyApplicationService
from property_service.application.services.property_import_service import PropertyImportService
from property_service.presentation.api.deps import get_import_service, get_property_service, require_permission
from property_service.presentation.api.helpers import response_meta
from property_service.presentation.schemas.bulk_schemas import (
    BulkDeleteRequest,
    BulkError,
    BulkImportRequest,
    BulkJobResponse,
    BulkUpdateRequest,
)
from property_service.presentation.schemas.common import ApiResponse

router = APIRouter(prefix="/properties/bulk", tags=["bulk-operations"])


@router.post("/import", status_code=202)
async def bulk_import(
    request: Request,
    body: BulkImportRequest,
    auth: AuthContext = Depends(require_permission("property:bulk_import")),
    import_service: PropertyImportService = Depends(get_import_service),
):
    job = await import_service.bulk_import(
        items_payload=[item.model_dump(mode="json") for item in body.items],
        source_type=body.source_type,
        auth=auth,
        async_mode=body.options.async_mode,
        skip_duplicates=body.options.skip_duplicates,
        auto_geocode=body.options.auto_geocode,
        default_status=body.options.default_status,
    )
    return JSONResponse(
        status_code=202,
        content=ApiResponse(
            data=BulkJobResponse(
                job_id=job.job_id,
                status=job.status,
                total_items=job.total_items,
                processed=job.processed_items,
                failed=len(job.errors),
                errors=[BulkError(index=i, message=msg) for i, msg in enumerate(job.errors)],
            ).model_dump(),
            meta=response_meta(request),
        ).model_dump(),
    )


@router.patch("/update", status_code=202)
async def bulk_update(
    request: Request,
    body: BulkUpdateRequest,
    auth: AuthContext = Depends(require_permission("property:bulk_update")),
):
    job_id = UUID(int=0)
    return JSONResponse(
        status_code=202,
        content=ApiResponse(
            data=BulkJobResponse(job_id=job_id, status="queued", total_items=0).model_dump(),
            meta=response_meta(request),
        ).model_dump(),
    )


@router.delete("")
async def bulk_delete(
    request: Request,
    body: BulkDeleteRequest,
    auth: AuthContext = Depends(require_permission("property:bulk_delete")),
    service: PropertyApplicationService = Depends(get_property_service),
):
    deleted = await service.bulk_delete(body.property_ids, auth)
    return ApiResponse(data={"deleted_count": deleted}, meta=response_meta(request))


@router.get("/jobs/{job_id}")
async def bulk_job_status(
    request: Request,
    job_id: UUID,
    import_service: PropertyImportService = Depends(get_import_service),
):
    job = await import_service.get_job(job_id)
    if job is None:
        return ApiResponse(data={"job_id": str(job_id), "status": "not_found"}, meta=response_meta(request))
    return ApiResponse(
        data=BulkJobResponse(
            job_id=job.job_id,
            status=job.status,
            total_items=job.total_items,
            processed=job.processed_items,
            failed=len(job.errors),
            errors=[BulkError(index=i, message=msg) for i, msg in enumerate(job.errors)],
        ).model_dump(),
        meta=response_meta(request),
    )
