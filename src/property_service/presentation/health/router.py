from __future__ import annotations

from fastapi import APIRouter
from fastapi.responses import JSONResponse

from property_service.presentation.health.checks import run_readiness_checks, run_startup_checks

router = APIRouter(tags=["health"])


@router.get("/health")
async def liveness() -> dict[str, str]:
    return {"status": "ok"}


@router.get("/health/ready")
async def readiness() -> JSONResponse:
    checks, ready = await run_readiness_checks()
    return JSONResponse(
        status_code=200 if ready else 503,
        content={"status": "ready" if ready else "not_ready", **checks},
    )


@router.get("/health/startup")
async def startup() -> JSONResponse:
    checks, started = await run_startup_checks()
    return JSONResponse(
        status_code=200 if started else 503,
        content={"status": "started" if started else "starting", **checks},
    )
