#!/usr/bin/env python3
"""Seed demo listings into property-service (free local catalog; no Endeksa required).

Idempotent by title + tag `demo-seed`. Attaches Unsplash image URLs for UI cards.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import urllib.error
import urllib.request
import uuid
from typing import Any

API_BASE = os.environ.get("PROPERTY_API_BASE", "http://localhost:8001/api/v1").rstrip("/")
DEMO_TAG = "demo-seed"
COMPOSE_FILE = os.environ.get(
    "COMPOSE_FILE",
    os.path.join(os.path.dirname(__file__), "..", "docker", "docker-compose.yml"),
)

# Royalty-free Unsplash photos (stable image IDs) — demo only.
_IMG = {
    "residence": "https://images.unsplash.com/photo-1502672260266-1c1ef2d93688?auto=format&fit=crop&w=1200&q=80",
    "apartment": "https://images.unsplash.com/photo-1522708323590-d24dbb6b0267?auto=format&fit=crop&w=1200&q=80",
    "villa": "https://images.unsplash.com/photo-1613490493576-7fde63acd811?auto=format&fit=crop&w=1200&q=80",
    "office": "https://images.unsplash.com/photo-1497366216548-37526070297c?auto=format&fit=crop&w=1200&q=80",
    "land": "https://images.unsplash.com/photo-1500382017468-9049fed747ef?auto=format&fit=crop&w=1200&q=80",
    "store": "https://images.unsplash.com/photo-1441986300917-64674bd600d8?auto=format&fit=crop&w=1200&q=80",
}

DEMO_PROPERTIES: list[dict[str, Any]] = [
    {
        "title": "Beşiktaş Boğaz Manzaralı Residence",
        "description": "Torkam portföyü — deniz manzaralı 3+1 residence. Yatırım ve oturum için uygun.",
        "property_type": "residence",
        "property_category": "residential",
        "status": "active",
        "visibility": "tenant",
        "pricing": {"sale_price": "18500000.00", "currency": "TRY"},
        "location": {
            "country_code": "TR",
            "province": "İstanbul",
            "district": "Beşiktaş",
            "neighborhood": "Levent",
            "street": "Büyükdere Cad.",
            "latitude": "41.081200",
            "longitude": "29.012300",
        },
        "building": {
            "construction_year": 2019,
            "floor_count": 28,
            "floor_number": 18,
            "net_area_sqm": "165.00",
            "gross_area_sqm": "195.00",
            "room_count": "3.5",
            "bedroom_count": 3,
            "bathroom_count": 2,
            "balcony_count": 2,
            "parking_count": 1,
        },
        "features": {
            "heating_type": "central",
            "has_elevator": True,
            "has_parking": True,
            "has_balcony": True,
            "has_security": True,
            "has_smart_home": True,
        },
        "amenities": ["parking", "security", "elevator", "gym"],
        "tags": [DEMO_TAG, "istanbul", "sea-view"],
        "image_url": _IMG["residence"],
    },
    {
        "title": "Kadıköy Moda Teraslı Daire",
        "description": "Moda'ya yakın, teraslı 2+1 daire. Kiralık portföy varlığı.",
        "property_type": "apartment",
        "property_category": "residential",
        "status": "active",
        "visibility": "tenant",
        "pricing": {"sale_price": "9200000.00", "rental_price": "65000.00", "currency": "TRY"},
        "location": {
            "country_code": "TR",
            "province": "İstanbul",
            "district": "Kadıköy",
            "neighborhood": "Moda",
            "latitude": "40.984500",
            "longitude": "29.025100",
        },
        "building": {
            "construction_year": 2012,
            "floor_count": 6,
            "floor_number": 4,
            "net_area_sqm": "98.00",
            "room_count": "2.5",
            "bedroom_count": 2,
            "bathroom_count": 1,
            "balcony_count": 1,
        },
        "features": {
            "heating_type": "combi",
            "has_elevator": True,
            "has_balcony": True,
        },
        "amenities": ["elevator", "parking"],
        "tags": [DEMO_TAG, "istanbul", "rental"],
        "image_url": _IMG["apartment"],
    },
    {
        "title": "Çankaya Villa — Bahçeli",
        "description": "Ankara Çankaya'da müstakil villa, geniş bahçe ve havuz.",
        "property_type": "villa",
        "property_category": "residential",
        "status": "active",
        "visibility": "tenant",
        "pricing": {"sale_price": "27500000.00", "currency": "TRY"},
        "location": {
            "country_code": "TR",
            "province": "Ankara",
            "district": "Çankaya",
            "neighborhood": "Oran",
            "latitude": "39.890100",
            "longitude": "32.854200",
        },
        "building": {
            "construction_year": 2016,
            "floor_count": 3,
            "net_area_sqm": "320.00",
            "gross_area_sqm": "380.00",
            "room_count": "5.5",
            "bedroom_count": 5,
            "bathroom_count": 4,
            "parking_count": 2,
        },
        "features": {
            "heating_type": "central",
            "has_parking": True,
            "has_garden": True,
            "has_pool": True,
            "has_security": True,
            "has_storage": True,
        },
        "amenities": ["pool", "parking", "security"],
        "tags": [DEMO_TAG, "ankara", "villa"],
        "image_url": _IMG["villa"],
    },
    {
        "title": "Bornova Ofis Katı",
        "description": "İzmir Bornova'da A sınıfı ofis katı — ticari portföy.",
        "property_type": "office",
        "property_category": "commercial",
        "status": "active",
        "visibility": "tenant",
        "pricing": {"sale_price": "14800000.00", "rental_price": "180000.00", "currency": "TRY"},
        "location": {
            "country_code": "TR",
            "province": "İzmir",
            "district": "Bornova",
            "neighborhood": "Erzene",
            "latitude": "38.462800",
            "longitude": "27.220500",
        },
        "building": {
            "construction_year": 2020,
            "floor_count": 12,
            "floor_number": 7,
            "net_area_sqm": "240.00",
            "gross_area_sqm": "280.00",
            "parking_count": 4,
        },
        "features": {
            "cooling_type": "vrv",
            "has_elevator": True,
            "has_parking": True,
            "has_security": True,
        },
        "amenities": ["parking", "security", "elevator"],
        "tags": [DEMO_TAG, "izmir", "commercial"],
        "image_url": _IMG["office"],
    },
    {
        "title": "Bodrum Yalıkavak Arsa",
        "description": "Yalıkavak'ta imarlı arsa — proje geliştirme adayı.",
        "property_type": "land",
        "property_category": "land",
        "status": "draft",
        "visibility": "private",
        "pricing": {"sale_price": "42000000.00", "currency": "TRY"},
        "location": {
            "country_code": "TR",
            "province": "Muğla",
            "district": "Bodrum",
            "neighborhood": "Yalıkavak",
            "latitude": "37.105600",
            "longitude": "27.288900",
        },
        "parcel": {
            "block": "312",
            "parcel_number": "14",
            "parcel_area_sqm": "1250.00",
            "zoning_type": "residential",
        },
        "amenities": [],
        "tags": [DEMO_TAG, "bodrum", "development"],
        "image_url": _IMG["land"],
    },
    {
        "title": "Ataşehir Residence Stüdyo",
        "description": "Merkezi konumda stüdyo — kiralık portföy.",
        "property_type": "apartment",
        "property_category": "residential",
        "status": "active",
        "visibility": "tenant",
        "pricing": {"sale_price": "4500000.00", "rental_price": "32000.00", "currency": "TRY"},
        "location": {
            "country_code": "TR",
            "province": "İstanbul",
            "district": "Ataşehir",
            "neighborhood": "Barbaros",
            "latitude": "40.992300",
            "longitude": "29.127800",
        },
        "building": {
            "construction_year": 2021,
            "floor_count": 20,
            "floor_number": 9,
            "net_area_sqm": "48.00",
            "room_count": "1.0",
            "bedroom_count": 1,
            "bathroom_count": 1,
        },
        "features": {
            "has_elevator": True,
            "has_parking": True,
            "has_security": True,
            "has_smart_home": True,
        },
        "amenities": ["parking", "security", "elevator", "gym"],
        "tags": [DEMO_TAG, "istanbul", "studio"],
        "image_url": _IMG["apartment"],
    },
    {
        "title": "Nişantaşı Butik Daire",
        "description": "Nişantaşı'nda yenilenmiş 2+1 — prestijli konum.",
        "property_type": "apartment",
        "property_category": "residential",
        "status": "active",
        "visibility": "tenant",
        "pricing": {"sale_price": "16800000.00", "currency": "TRY"},
        "location": {
            "country_code": "TR",
            "province": "İstanbul",
            "district": "Şişli",
            "neighborhood": "Nişantaşı",
            "latitude": "41.051800",
            "longitude": "28.994600",
        },
        "building": {
            "construction_year": 2008,
            "floor_count": 7,
            "floor_number": 3,
            "net_area_sqm": "110.00",
            "room_count": "2.5",
            "bedroom_count": 2,
            "bathroom_count": 2,
        },
        "features": {"heating_type": "combi", "has_elevator": True, "has_balcony": True},
        "amenities": ["elevator", "security"],
        "tags": [DEMO_TAG, "istanbul", "nisantasi"],
        "image_url": _IMG["apartment"],
    },
    {
        "title": "Bağdat Caddesi Cadde Dükkanı",
        "description": "Kadıköy Bağdat Cad. üzeri vitrinli dükkan.",
        "property_type": "store",
        "property_category": "commercial",
        "status": "active",
        "visibility": "tenant",
        "pricing": {"sale_price": "32000000.00", "rental_price": "420000.00", "currency": "TRY"},
        "location": {
            "country_code": "TR",
            "province": "İstanbul",
            "district": "Kadıköy",
            "neighborhood": "Caddebostan",
            "latitude": "40.966200",
            "longitude": "29.063400",
        },
        "building": {"net_area_sqm": "85.00", "floor_number": 0},
        "features": {"has_security": True},
        "amenities": ["security"],
        "tags": [DEMO_TAG, "istanbul", "retail"],
        "image_url": _IMG["store"],
    },
]


def _request(method: str, path: str, body: dict[str, Any] | None = None) -> dict[str, Any]:
    url = f"{API_BASE}{path}"
    data = None if body is None else json.dumps(body).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=data,
        method=method,
        headers={"Content-Type": "application/json", "Accept": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            raw = resp.read().decode("utf-8")
            return json.loads(raw) if raw else {}
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"{method} {path} -> {exc.code}: {detail}") from exc


def _existing_by_title() -> dict[str, str]:
    result = _request("GET", "/properties/search?page=1&page_size=100")
    items = result.get("data") or []
    return {str(item["title"]): str(item["id"]) for item in items if item.get("title") and item.get("id")}


def _set_status(property_id: str, version: int, status: str) -> int:
    result = _request(
        "POST",
        f"/properties/{property_id}/status",
        {"version": version, "status": status, "reason": "demo seed"},
    )
    return int((result.get("data") or {}).get("version") or version + 1)


def _activate(property_id: str, version: int, status: str) -> None:
    if status == "draft":
        return
    if status == "listed":
        version = _set_status(property_id, version, "active")
        _set_status(property_id, version, "listed")
        return
    _set_status(property_id, version, status)


def _attach_image_via_sql(property_id: str, image_url: str, caption: str) -> None:
    """Insert a ready image row (avoids S3 upload for local demo)."""
    image_id = str(uuid.uuid4())
    storage_key = f"demo/{property_id}/{image_id}.jpg"
    # Escape single quotes for SQL
    safe_url = image_url.replace("'", "''")
    safe_caption = caption.replace("'", "''")
    sql = f"""
    INSERT INTO property.property_images (
      id, property_id, storage_key, url, thumbnail_url, caption,
      sort_order, is_primary, mime_type, processing_status
    )
    SELECT
      '{image_id}'::uuid,
      '{property_id}'::uuid,
      '{storage_key}',
      '{safe_url}',
      '{safe_url}',
      '{safe_caption}',
      0,
      true,
      'image/jpeg',
      'ready'
    WHERE NOT EXISTS (
      SELECT 1 FROM property.property_images
      WHERE property_id = '{property_id}'::uuid
        AND is_primary = true
        AND deleted_at IS NULL
    );
    """
    cmd = [
        "docker",
        "compose",
        "-f",
        os.path.abspath(COMPOSE_FILE),
        "exec",
        "-T",
        "postgres",
        "psql",
        "-U",
        "property",
        "-d",
        "property_db",
        "-v",
        "ON_ERROR_STOP=1",
        "-c",
        sql,
    ]
    try:
        subprocess.run(cmd, check=True, capture_output=True, text=True)
    except (subprocess.CalledProcessError, FileNotFoundError) as exc:
        print(f"  warn image attach for {property_id}: {exc}")


def seed() -> int:
    print(f"Seeding free demo listings via {API_BASE}")
    print("(Endeksa is paid — using property-service catalog for now)")
    existing = _existing_by_title()
    created = 0
    skipped = 0
    imaged = 0

    for item in DEMO_PROPERTIES:
        title = item["title"]
        image_url = item.get("image_url")
        if title in existing:
            print(f"  skip (exists): {title}")
            skipped += 1
            prop_id = existing[title]
        else:
            desired_status = item.get("status", "draft")
            create_body = {k: v for k, v in item.items() if k != "image_url"}
            create_body["status"] = "draft"
            result = _request("POST", "/properties", create_body)
            prop = result.get("data") or {}
            prop_id = prop.get("id")
            version = int(prop.get("version") or 1)
            if not prop_id:
                raise RuntimeError(f"Create returned no id for {title}: {result}")
            try:
                _activate(str(prop_id), version, str(desired_status))
            except RuntimeError as exc:
                print(f"  warn status for {title}: {exc}")
            print(f"  created: {title} ({prop_id})")
            created += 1
            existing[title] = str(prop_id)

        if image_url and prop_id:
            _attach_image_via_sql(str(prop_id), str(image_url), title)
            imaged += 1

    print(f"Done. created={created} skipped={skipped} images_ensured={imaged}")
    return 0 if created or skipped else 1


if __name__ == "__main__":
    try:
        raise SystemExit(seed())
    except Exception as exc:  # noqa: BLE001
        print(f"seed_demo_properties failed: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc
