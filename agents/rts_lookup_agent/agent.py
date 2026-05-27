"""RTSLookupAgent — coordinates three parallel real-time lookups.

Within a single case stage we fan out to:
  - AED locator (OSM Overpass)
  - Drug interactions (RxNav)
  - Ambulance ETA (mock now)

The three are independent, so we parallelize with `concurrent.futures`.
Soft failures of any one branch surface in `result.warnings`, never block
the case.
"""
from __future__ import annotations

import concurrent.futures
import os

from . import aed as aed_mod
from . import ambulance as ambulance_mod
from . import drug as drug_mod
from .models import (
    AedLocation,
    AmbulanceEta,
    DrugInteraction,
    RTSLookupRequest,
    RTSLookupResult,
)
from ..shared.logging import get_logger

logger = get_logger("rts_lookup_agent")


def _safe(fn, label: str, warnings: list[str]):
    """Run `fn`, capture exceptions into warnings, return value or None."""
    try:
        return fn()
    except Exception as e:
        msg = f"{label} failed: {type(e).__name__}: {e}"
        logger.warning(msg)
        warnings.append(msg)
        return None


class RTSLookupAgent:
    """Parallel RTS lookup orchestrator for Stage 2."""

    def __init__(self, *, max_workers: int = 4):
        self.max_workers = max_workers

    def lookup(self, request: RTSLookupRequest) -> RTSLookupResult:
        logger.info(
            f"Stage 2 lookup: case={request.case_id} loc=({request.location.lat:.4f},"
            f"{request.location.lon:.4f}) radius={request.aed_radius_m}m"
        )

        warnings: list[str] = []

        with concurrent.futures.ThreadPoolExecutor(
            max_workers=self.max_workers
        ) as pool:
            f_aed = pool.submit(
                _safe,
                lambda: aed_mod.find_nearby_aeds(
                    request.location.lat,
                    request.location.lon,
                    request.aed_radius_m,
                ),
                "aed",
                warnings,
            )
            drug_inputs = list(set(request.medications + request.proposed_treatments))
            f_drug = pool.submit(
                _safe,
                lambda: drug_mod.check_interactions(drug_inputs),
                "drug",
                warnings,
            )
            f_ambulance = pool.submit(
                _safe,
                lambda: ambulance_mod.get_eta(
                    request.location, case_id=request.case_id
                ),
                "ambulance",
                warnings,
            )

        aeds: list[AedLocation] = f_aed.result() or []
        drugs: list[DrugInteraction] = f_drug.result() or []
        ambulance: AmbulanceEta | None = f_ambulance.result()

        result = RTSLookupResult(
            case_id=request.case_id,
            aeds=aeds,
            drug_interactions=drugs,
            ambulance=ambulance,
            warnings=warnings,
        )

        logger.info(
            f"Lookup done: aeds={len(aeds)} drug_interactions={len(drugs)} "
            f"ambulance={'yes' if ambulance else 'no'} warnings={len(warnings)}"
        )
        return result
