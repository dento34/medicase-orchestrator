"""Ambulance ETA — mock during hackathon, swap to event-ops API in production.

Production replacement would call the venue's ambulance dispatch system.
For demo + tests, returns a deterministic, plausible ETA.
"""
from __future__ import annotations

import os
import random

from .models import AmbulanceEta, GeoPoint
from ..shared.logging import get_logger

logger = get_logger("ambulance")


def get_eta(location: GeoPoint, *, case_id: str | None = None) -> AmbulanceEta:
    """Return an ambulance ETA.

    Demo mode: deterministic per case_id (so repeated runs of the demo
    are reproducible). Production mode: this is where you'd call the
    venue's dispatch API.
    """
    api_url = os.getenv("AMBULANCE_API_URL", "")
    if api_url and "localhost" not in api_url and "mock" not in api_url:
        # Future: real API integration goes here.
        logger.warning(
            "Real ambulance API requested but no implementation yet — "
            "falling back to mock."
        )

    seed = hash(case_id) if case_id else hash((location.lat, location.lon))
    rng = random.Random(seed)
    eta = rng.randint(3, 9)
    confidence = round(rng.uniform(0.70, 0.95), 2)
    unit_id = f"AMB-{abs(seed) % 1000:03d}"

    logger.info(f"Ambulance ETA: {eta} min (unit={unit_id}, conf={confidence})")
    return AmbulanceEta(
        eta_minutes=eta, confidence=confidence, unit_id=unit_id, source="mock"
    )
