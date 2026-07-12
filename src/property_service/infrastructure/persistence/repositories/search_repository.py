from __future__ import annotations

from math import cos, radians
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import noload
from sqlalchemy.ext.asyncio import AsyncSession

from property_service.application.dto.property_search_dto import (
    MapCluster,
    MapSearchCriteria,
    NearbySearchCriteria,
    PropertySearchCriteria,
    PropertySearchResult,
    PropertySummary,
)
from property_service.domain.repositories.property_search_repository import IPropertySearchRepository
from property_service.infrastructure.persistence.mappers.search_mapper import SearchMapper
from property_service.infrastructure.persistence.models import PropertyModel


class SqlAlchemySearchRepository(IPropertySearchRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def search(self, criteria: PropertySearchCriteria, tenant_id: UUID) -> PropertySearchResult:
        stmt = select(PropertyModel).options(noload(PropertyModel.images)).where(
            PropertyModel.tenant_id == tenant_id,
            PropertyModel.deleted_at.is_(None),
        )
        filters = criteria.filters_dict

        if criteria.query:
            q = f"%{criteria.query}%"
            stmt = stmt.where(
                PropertyModel.title.ilike(q)
                | PropertyModel.description.ilike(q)
                | PropertyModel.province.ilike(q)
                | PropertyModel.district.ilike(q)
            )

        if types := filters.get("property_types"):
            stmt = stmt.where(PropertyModel.property_type.in_(types))
        if statuses := filters.get("status"):
            stmt = stmt.where(PropertyModel.status.in_(statuses))
        if country := filters.get("country_code"):
            stmt = stmt.where(PropertyModel.country_code == country)
        if provinces := filters.get("provinces"):
            stmt = stmt.where(PropertyModel.province.in_(provinces))
        if districts := filters.get("districts"):
            stmt = stmt.where(PropertyModel.district.in_(districts))

        price = filters.get("sale_price") or {}
        if price.get("min") is not None:
            stmt = stmt.where(PropertyModel.sale_price >= price["min"])
        if price.get("max") is not None:
            stmt = stmt.where(PropertyModel.sale_price <= price["max"])

        area = filters.get("net_area_sqm") or {}
        if area.get("min") is not None:
            stmt = stmt.where(PropertyModel.net_area_sqm >= area["min"])
        if area.get("max") is not None:
            stmt = stmt.where(PropertyModel.net_area_sqm <= area["max"])

        rooms = filters.get("room_count") or {}
        if rooms.get("min") is not None:
            stmt = stmt.where(PropertyModel.room_count >= rooms["min"])
        if rooms.get("max") is not None:
            stmt = stmt.where(PropertyModel.room_count <= rooms["max"])

        if geo := criteria.geo_dict:
            stmt = self._apply_geo(stmt, geo)

        sort_field = criteria.sort[0].field if criteria.sort else "created_at"
        sort_dir = criteria.sort[0].direction if criteria.sort else "desc"
        col = getattr(PropertyModel, sort_field, PropertyModel.created_at)
        stmt = stmt.order_by(col.desc() if sort_dir == "desc" else col.asc())

        count_stmt = select(func.count()).select_from(stmt.subquery())
        total = (await self._session.execute(count_stmt)).scalar_one()

        stmt = stmt.offset((criteria.page - 1) * criteria.page_size).limit(criteria.page_size)
        rows = (await self._session.execute(stmt)).scalars().all()

        items = [SearchMapper.to_summary(r) for r in rows]
        facets = None
        if criteria.include_facets:
            facets = await self._facets(tenant_id)

        return PropertySearchResult(
            items=items,
            total=total,
            page=criteria.page,
            page_size=criteria.page_size,
            facets=facets,
        )

    async def find_nearby(
        self,
        criteria: NearbySearchCriteria,
        tenant_id: UUID,
    ) -> PropertySearchResult:
        lat_delta = criteria.radius_meters / 111_000
        lng_delta = criteria.radius_meters / (
            111_000 * max(abs(cos(radians(criteria.latitude))), 0.01)
        )

        stmt = select(PropertyModel).where(
            PropertyModel.tenant_id == tenant_id,
            PropertyModel.deleted_at.is_(None),
            PropertyModel.latitude.isnot(None),
            PropertyModel.longitude.isnot(None),
            PropertyModel.latitude.between(criteria.latitude - lat_delta, criteria.latitude + lat_delta),
            PropertyModel.longitude.between(criteria.longitude - lng_delta, criteria.longitude + lng_delta),
        )
        if criteria.property_type:
            stmt = stmt.where(PropertyModel.property_type == criteria.property_type)
        if criteria.status:
            stmt = stmt.where(PropertyModel.status.in_(criteria.status))

        rows = (await self._session.execute(stmt.limit(criteria.limit * 3))).scalars().all()
        items: list[PropertySummary] = []
        for row in rows:
            dist = self._haversine_meters(
                criteria.latitude,
                criteria.longitude,
                float(row.latitude),
                float(row.longitude),
            )
            if dist <= criteria.radius_meters:
                summary = SearchMapper.to_summary(row)
                summary.distance_meters = dist
                items.append(summary)
        items.sort(key=lambda item: item.distance_meters or 0)
        items = items[: criteria.limit]
        return PropertySearchResult(items=items, total=len(items), page=1, page_size=criteria.limit)

    async def map_search(
        self,
        criteria: MapSearchCriteria,
        tenant_id: UUID,
    ) -> list[MapCluster | PropertySummary]:
        stmt = (
            select(PropertyModel)
            .where(
                PropertyModel.tenant_id == tenant_id,
                PropertyModel.deleted_at.is_(None),
                PropertyModel.latitude.isnot(None),
                PropertyModel.longitude.isnot(None),
                PropertyModel.latitude.between(criteria.south, criteria.north),
                PropertyModel.longitude.between(criteria.west, criteria.east),
            )
            .limit(criteria.limit)
        )
        rows = (await self._session.execute(stmt)).scalars().all()
        summaries = [SearchMapper.to_summary(row) for row in rows]
        if criteria.cluster and criteria.zoom < 14:
            return self._cluster_summaries(summaries, criteria.zoom)
        return summaries

    async def get_statistics(
        self,
        tenant_id: UUID,
        *,
        group_by: list[str] | None = None,
    ) -> PropertyStatistics:
        total = await self.count_by_tenant(tenant_id)
        by_status = await self._group_count(tenant_id, PropertyModel.status)
        by_type = await self._group_count(tenant_id, PropertyModel.property_type)
        by_province = await self._group_count(tenant_id, PropertyModel.province)

        price_stmt = select(
            func.avg(PropertyModel.sale_price),
            func.min(PropertyModel.sale_price),
            func.max(PropertyModel.sale_price),
        ).where(
            PropertyModel.tenant_id == tenant_id,
            PropertyModel.deleted_at.is_(None),
            PropertyModel.sale_price.isnot(None),
        )
        avg_p, min_p, max_p = (await self._session.execute(price_stmt)).one()

        grouped: dict[str, dict[str, int]] = {}
        if group_by:
            column_map = {
                "status": PropertyModel.status,
                "type": PropertyModel.property_type,
                "property_type": PropertyModel.property_type,
                "province": PropertyModel.province,
            }
            for field in group_by:
                column = column_map.get(field)
                if column is not None:
                    grouped[field] = await self._group_count(tenant_id, column)

        return PropertyStatistics(
            total_count=total,
            by_status=by_status,
            by_type=by_type,
            by_province=by_province,
            price_stats={
                "avg_sale_price": float(avg_p) if avg_p else None,
                "min_sale_price": float(min_p) if min_p else None,
                "max_sale_price": float(max_p) if max_p else None,
            },
            grouped=grouped,
        )

    async def count_by_tenant(self, tenant_id: UUID) -> int:
        stmt = select(func.count()).select_from(PropertyModel).where(
            PropertyModel.tenant_id == tenant_id,
            PropertyModel.deleted_at.is_(None),
        )
        return (await self._session.execute(stmt)).scalar_one()

    async def price_distribution(self, tenant_id: UUID) -> dict:
        stmt = (
            select(PropertyModel.sale_price)
            .where(
                PropertyModel.tenant_id == tenant_id,
                PropertyModel.deleted_at.is_(None),
                PropertyModel.sale_price.isnot(None),
            )
            .order_by(PropertyModel.sale_price)
        )
        prices = [float(row[0]) for row in (await self._session.execute(stmt)).all()]
        if not prices:
            return {"count": 0, "min": None, "max": None, "avg": None, "median": None}

        count = len(prices)
        median = prices[count // 2] if count % 2 else (prices[count // 2 - 1] + prices[count // 2]) / 2
        return {
            "count": count,
            "min": prices[0],
            "max": prices[-1],
            "avg": sum(prices) / count,
            "median": median,
        }

    async def _group_count(self, tenant_id: UUID, column) -> dict:
        stmt = (
            select(column, func.count())
            .where(PropertyModel.tenant_id == tenant_id, PropertyModel.deleted_at.is_(None))
            .group_by(column)
        )
        rows = await self._session.execute(stmt)
        return {str(k): v for k, v in rows.all() if k is not None}

    async def _facets(self, tenant_id: UUID) -> dict:
        return {
            "status": await self._group_count(tenant_id, PropertyModel.status),
            "property_type": await self._group_count(tenant_id, PropertyModel.property_type),
            "province": await self._group_count(tenant_id, PropertyModel.province),
        }

    @staticmethod
    def _cluster_summaries(summaries: list[PropertySummary], zoom: int) -> list[MapCluster]:
        if not summaries:
            return []
        cell = max(0.01, 0.5 / max(zoom, 1))
        buckets: dict[tuple[int, int], list[PropertySummary]] = {}
        for summary in summaries:
            if summary.latitude is None or summary.longitude is None:
                continue
            lat = float(summary.latitude)
            lng = float(summary.longitude)
            key = (int(lat / cell), int(lng / cell))
            buckets.setdefault(key, []).append(summary)
        clusters: list[MapCluster] = []
        for bucket in buckets.values():
            lat_avg = sum(float(item.latitude) for item in bucket) / len(bucket)
            lng_avg = sum(float(item.longitude) for item in bucket) / len(bucket)
            clusters.append(
                MapCluster(
                    latitude=lat_avg,
                    longitude=lng_avg,
                    count=len(bucket),
                    property_ids=[str(item.id) for item in bucket if item.id],
                )
            )
        return clusters

    @staticmethod
    def _apply_geo(stmt, geo: dict):
        if geo.get("type") == "bounding_box":
            return stmt.where(
                PropertyModel.latitude.between(geo["south"], geo["north"]),
                PropertyModel.longitude.between(geo["west"], geo["east"]),
            )
        if geo.get("type") == "radius":
            lat, lng = geo["latitude"], geo["longitude"]
            radius = geo["radius_meters"]
            lat_delta = radius / 111_000
            lng_delta = radius / (111_000 * max(abs(cos(radians(float(lat)))), 0.01))
            return stmt.where(
                PropertyModel.latitude.between(float(lat) - lat_delta, float(lat) + lat_delta),
                PropertyModel.longitude.between(float(lng) - lng_delta, float(lng) + lng_delta),
            )
        return stmt

    @staticmethod
    def _haversine_meters(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
        from math import asin, sin, sqrt

        r = 6_371_000
        dlat = radians(lat2 - lat1)
        dlng = radians(lng2 - lng1)
        a = sin(dlat / 2) ** 2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlng / 2) ** 2
        return 2 * r * asin(sqrt(a))
