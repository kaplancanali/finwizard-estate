from __future__ import annotations

import pytest


@pytest.mark.asyncio
async def test_liveness(client):
    response = await client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


@pytest.mark.asyncio
async def test_readiness(client):
    response = await client.get("/health/ready")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ready"
    assert body["database"] == "ok"
    assert body["redis"] == "skipped"
    assert body["rabbitmq"] == "skipped"


@pytest.mark.asyncio
async def test_startup(client):
    response = await client.get("/health/startup")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "started"
    assert body["startup"] == "ok"
    assert body["lookups"] == "ok"
