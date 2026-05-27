"""RTSLookupAgent — Stage 2 (Stabilization): real-time resource discovery.

Three parallel lookups during a case:
  - Nearest AED (OpenStreetMap Overpass API)
  - Drug interactions (NIH RxNav API)
  - Ambulance ETA (mock during hackathon; event-ops API in production)
"""
from .agent import RTSLookupAgent
from .models import (
    AedLocation,
    AmbulanceEta,
    DrugInteraction,
    RTSLookupRequest,
    RTSLookupResult,
)

__all__ = [
    "RTSLookupAgent",
    "AedLocation",
    "AmbulanceEta",
    "DrugInteraction",
    "RTSLookupRequest",
    "RTSLookupResult",
]
