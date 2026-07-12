from __future__ import annotations

import pytest

SAMPLE_PROPERTY = {
    "title": "Modern Apartment in Kadikoy",
    "description": "Spacious apartment",
    "property_type": "apartment",
    "property_category": "residential",
    "pricing": {"sale_price": 5000000, "currency": "TRY"},
    "location": {
        "country_code": "TR",
        "province": "Istanbul",
        "district": "Kadikoy",
        "latitude": 40.9876,
        "longitude": 29.0234,
    },
    "building": {"net_area_sqm": 120, "room_count": 3, "bathroom_count": 2},
}


@pytest.mark.asyncio
async def test_health(client):
    response = await client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


@pytest.mark.asyncio
async def test_create_and_get_property(client):
    create_resp = await client.post("/api/v1/properties", json=SAMPLE_PROPERTY)
    assert create_resp.status_code == 201
    body = create_resp.json()["data"]
    assert body["title"] == SAMPLE_PROPERTY["title"]
    assert body["property_code"].startswith("FW-TR-")

    prop_id = body["id"]
    get_resp = await client.get(f"/api/v1/properties/{prop_id}")
    assert get_resp.status_code == 200
    assert get_resp.json()["data"]["id"] == prop_id


@pytest.mark.asyncio
async def test_search_properties(client):
    await client.post("/api/v1/properties", json=SAMPLE_PROPERTY)
    search_resp = await client.post(
        "/api/v1/properties/search",
        json={"query": "Modern", "page": 1, "page_size": 10},
    )
    assert search_resp.status_code == 200
    data = search_resp.json()
    assert data["pagination"]["total_items"] >= 1


@pytest.mark.asyncio
async def test_change_status_flow(client):
    create_resp = await client.post("/api/v1/properties", json=SAMPLE_PROPERTY)
    prop = create_resp.json()["data"]

    status_resp = await client.post(
        f"/api/v1/properties/{prop['id']}/status",
        json={"version": prop["version"], "status": "active"},
    )
    assert status_resp.status_code == 200
    assert status_resp.json()["data"]["status"] == "active"


@pytest.mark.asyncio
async def test_soft_delete_and_restore(client):
    create_resp = await client.post("/api/v1/properties", json=SAMPLE_PROPERTY)
    prop = create_resp.json()["data"]

    del_resp = await client.delete(f"/api/v1/properties/{prop['id']}")
    assert del_resp.status_code == 204

    restore_resp = await client.post(f"/api/v1/properties/{prop['id']}/restore")
    assert restore_resp.status_code == 200
    assert restore_resp.json()["data"]["status"] == "draft"
