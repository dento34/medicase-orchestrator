"""AED (defibrillator) location lookup via OpenStreetMap Overpass API.

Overpass is free, no key required.
Endpoint: https://overpass-api.de/api/interpreter
"""
from __future__ import annotations

import json
import math
import os
import urllib.parse
import urllib.request

from .models import AedLocation
from ..shared.logging import get_logger

logger = get_logger("aed")

DEFAULT_OVERPASS_URL = "https://overpass-api.de/api/interpreter"
FALLBACK_OVERPASS_URLS = [
    "https://overpass.kumi.systems/api/interpreter",
    "https://overpass.openstreetmap.fr/api/interpreter",
]


def _haversine_m(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Great-circle distance between two points in meters."""
    r = 6_371_000.0
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(p1) * math.cos(p2) * math.sin(dlon / 2) ** 2
    )
    return 2 * r * math.asin(math.sqrt(a))


def _build_overpass_query(lat: float, lon: float, radius_m: int) -> str:
    """Overpass QL query for AED nodes within radius."""
    return (
        f"[out:json][timeout:20];"
        f'(node["emergency"="defibrillator"](around:{radius_m},{lat},{lon});'
        f' node["medical"="defibrillator"](around:{radius_m},{lat},{lon}););'
        f"out body;"
    )


def find_nearby_aeds(
    lat: float,
    lon: float,
    radius_m: int = 200,
    *,
    overpass_url: str | None = None,
    timeout_s: int = 25,
) -> list[AedLocation]:
    """Query OSM for defibrillators within `radius_m` of (lat, lon).

    Returns AedLocation list sorted by distance ascending.
    Raises on transport/parse failure; the agent above logs + degrades.
    """
    candidates = [
        overpass_url or os.getenv("OSM_OVERPASS_URL") or DEFAULT_OVERPASS_URL,
        *FALLBACK_OVERPASS_URLS,
    ]
    # de-duplicate while preserving order
    seen = set()
    candidates = [c for c in candidates if not (c in seen or seen.add(c))]

    query = _build_overpass_query(lat, lon, radius_m)
    logger.info(
        f"Overpass query: AEDs within {radius_m}m of ({lat:.5f}, {lon:.5f})"
    )

    data = urllib.parse.urlencode({"data": query}).encode("utf-8")
    last_exc: Exception | None = None
    payload: dict | None = None

    for url in candidates:
        req = urllib.request.Request(
            url,
            data=data,
            method="POST",
            headers={
                "Content-Type": "application/x-www-form-urlencoded",
                "User-Agent": "MediCase-Orchestrator/0.1 (UiPath AgentHack)",
            },
        )
        try:
            with urllib.request.urlopen(req, timeout=timeout_s) as resp:
                body = resp.read().decode("utf-8")
            payload = json.loads(body)
            logger.info(f"Overpass OK via {url}")
            break
        except Exception as e:
            logger.warning(f"Overpass failed at {url}: {e}; trying next instance")
            last_exc = e
            continue

    if payload is None:
        raise RuntimeError(
            f"All Overpass instances failed (last error: {last_exc!r})"
        )

    elements = payload.get("elements", [])

    results: list[AedLocation] = []
    for el in elements:
        if el.get("type") != "node":
            continue
        el_lat = el.get("lat")
        el_lon = el.get("lon")
        if el_lat is None or el_lon is None:
            continue
        tags = el.get("tags", {}) or {}
        results.append(
            AedLocation(
                osm_id=el.get("id"),
                lat=el_lat,
                lon=el_lon,
                distance_m=round(_haversine_m(lat, lon, el_lat, el_lon), 1),
                name=tags.get("name"),
                indoor=(tags.get("indoor") == "yes") if "indoor" in tags else None,
                access=tags.get("access"),
                description=tags.get("description"),
            )
        )

    results.sort(key=lambda a: a.distance_m)
    logger.info(f"Found {len(results)} AED(s) within {radius_m}m")
    return results
