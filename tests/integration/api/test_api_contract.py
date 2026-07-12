from __future__ import annotations

import pytest

from tests.integration.api.test_properties_api import SAMPLE_PROPERTY


@pytest.mark.asyncio
async def test_property_metadata_and_history(client):
    create_resp = await client.post("/api/v1/properties", json=SAMPLE_PROPERTY)
    prop_id = create_resp.json()["data"]["id"]

    meta_resp = await client.get(f"/api/v1/properties/{prop_id}/metadata")
    assert meta_resp.status_code == 200
    assert "metadata" in meta_resp.json()["data"]

    patch_resp = await client.patch(
        f"/api/v1/properties/{prop_id}/metadata",
        json={"metadata": {"custom_field": "EXT-1"}},
    )
    assert patch_resp.status_code == 200
    assert patch_resp.json()["data"]["metadata"]["custom_field"] == "EXT-1"

    price_hist = await client.get(f"/api/v1/properties/{prop_id}/history/price")
    assert price_hist.status_code == 200
    assert "pagination" in price_hist.json()
