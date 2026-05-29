"""Pydantic models for RTSLookupAgent."""
from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


# --------------------------------------------------------------- Inputs
class GeoPoint(BaseModel):
    lat: float = Field(..., ge=-90, le=90)
    lon: float = Field(..., ge=-180, le=180)


class RTSLookupRequest(BaseModel):
    """Inputs to the RTS lookup orchestrator."""

    case_id: str
    location: GeoPoint
    medications: list[str] = Field(
        default_factory=list,
        description="Patient-reported meds (free text, may include dosages)",
    )
    proposed_treatments: list[str] = Field(
        default_factory=list,
        description="Drugs we are considering administering on-site",
    )
    patient_conditions: list[str] = Field(
        default_factory=list,
        description="Chronic conditions; sharpens drug-interaction analysis",
    )
    aed_radius_m: int = 200


# --------------------------------------------------------------- AED
class AedLocation(BaseModel):
    """A defibrillator location returned from OpenStreetMap."""

    osm_id: int | None = None
    lat: float
    lon: float
    distance_m: float = Field(..., description="Distance from patient (meters)")
    name: str | None = None
    indoor: bool | None = None
    access: str | None = Field(default=None, description="OSM 'access' tag value")
    description: str | None = None


# --------------------------------------------------------------- Drugs
DrugInteractionSeverity = Literal["high", "moderate", "low", "n/a"]


class DrugInteraction(BaseModel):
    drug_a: str
    drug_b: str
    severity: DrugInteractionSeverity = "n/a"
    description: str
    source: str = Field(default="RxNav", description="Data source label")


# --------------------------------------------------------------- Ambulance
class AmbulanceEta(BaseModel):
    eta_minutes: int
    confidence: float = Field(..., ge=0.0, le=1.0)
    unit_id: str | None = None
    source: str = "mock"


# --------------------------------------------------------------- Result
class RTSLookupResult(BaseModel):
    """Unified output of the three parallel lookups."""

    case_id: str
    aeds: list[AedLocation] = Field(default_factory=list)
    drug_interactions: list[DrugInteraction] = Field(default_factory=list)
    ambulance: AmbulanceEta | None = None
    warnings: list[str] = Field(
        default_factory=list,
        description="Soft errors (e.g. one lookup failed) that didn't break the stage",
    )
