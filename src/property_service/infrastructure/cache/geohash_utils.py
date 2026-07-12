from __future__ import annotations

_BASE32 = "0123456789bcdefghjkmnpqrstuvwxyz"


def encode_geohash(latitude: float, longitude: float, precision: int = 5) -> str:
    lat_interval = [-90.0, 90.0]
    lon_interval = [-180.0, 180.0]
    geohash: list[str] = []
    bit = 0
    ch = 0
    even = True

    while len(geohash) < precision:
        if even:
            mid = (lon_interval[0] + lon_interval[1]) / 2
            if longitude > mid:
                ch |= 1 << (4 - bit)
                lon_interval[0] = mid
            else:
                lon_interval[1] = mid
        else:
            mid = (lat_interval[0] + lat_interval[1]) / 2
            if latitude > mid:
                ch |= 1 << (4 - bit)
                lat_interval[0] = mid
            else:
                lat_interval[1] = mid
        even = not even
        bit += 1
        if bit == 5:
            geohash.append(_BASE32[ch])
            bit = 0
            ch = 0
    return "".join(geohash)


def geohash_neighbors(geohash: str) -> list[str]:
    if not geohash:
        return []
    neighbors: set[str] = {geohash}
    # Approximate 8-neighbor grid by nudging decoded center.
    try:
        lat, lng = _decode_center(geohash)
        step = 0.01 / max(len(geohash), 1)
        for dlat in (-step, 0, step):
            for dlng in (-step, 0, step):
                neighbors.add(encode_geohash(lat + dlat, lng + dlng, precision=len(geohash)))
    except Exception:
        pass
    return sorted(neighbors)


def _decode_center(geohash: str) -> tuple[float, float]:
    lat_interval = [-90.0, 90.0]
    lon_interval = [-180.0, 180.0]
    even = True
    for char in geohash:
        cd = _BASE32.index(char)
        for mask in (16, 8, 4, 2, 1):
            if even:
                mid = (lon_interval[0] + lon_interval[1]) / 2
                if cd & mask:
                    lon_interval[0] = mid
                else:
                    lon_interval[1] = mid
            else:
                mid = (lat_interval[0] + lat_interval[1]) / 2
                if cd & mask:
                    lat_interval[0] = mid
                else:
                    lat_interval[1] = mid
            even = not even
    return (lat_interval[0] + lat_interval[1]) / 2, (lon_interval[0] + lon_interval[1]) / 2
