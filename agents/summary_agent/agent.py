"""SummaryAgent — assemble + render the Stage 3 handoff package."""
from __future__ import annotations

import json

from .models import HandoffReport, PatientSnapshot
from .prompts import CLINICAL_IMPRESSION_SYSTEM
from ..shared.llm import LLMClient
from ..shared.logging import get_logger

logger = get_logger("summary_agent")


def _or_unknown(value, fallback: str = "Unknown") -> str:
    if value is None:
        return fallback
    if isinstance(value, (list, tuple)):
        return ", ".join(str(v) for v in value) if value else fallback
    return str(value)


class SummaryAgent:
    """Builds the receiving-hospital handoff.

    Critical fields are template-driven. The LLM (if provided) only writes a
    clearly-labelled one-sentence clinical impression.
    """

    def __init__(self, llm: LLMClient | None = None):
        self.llm = llm  # optional; impression is skipped if None
        logger.info(
            f"SummaryAgent ready (llm={'yes' if llm else 'none'})"
        )

    def build_handoff(
        self,
        *,
        case_id: str,
        patient: PatientSnapshot,
        location: str | None = None,
        nearest_aed: str | None = None,
        ambulance_eta_min: int | None = None,
        drug_warnings: list[str] | None = None,
        handed_off_by: str | None = None,
        accepted_by: str | None = None,
        with_impression: bool = True,
    ) -> HandoffReport:
        report = HandoffReport(
            case_id=case_id,
            patient=patient,
            location=location,
            nearest_aed=nearest_aed,
            ambulance_eta_min=ambulance_eta_min,
            drug_warnings=drug_warnings or [],
            handed_off_by=handed_off_by,
            accepted_by=accepted_by,
        )
        if with_impression and self.llm is not None:
            try:
                report.clinical_impression = self._clinical_impression(report)
            except Exception as e:
                logger.warning(f"Clinical impression skipped: {e}")
        return report

    def _clinical_impression(self, report: HandoffReport) -> str:
        p = report.patient
        facts = {
            "age": p.approx_age,
            "sex": p.sex,
            "symptoms": p.symptoms,
            "pain_location": p.pain_location,
            "pain_scale": p.pain_scale,
            "allergies": p.allergies,
            "medications": p.medications,
            "chronic_conditions": p.chronic_conditions,
            "wearable": p.wearable_snapshot,
        }
        user = "Patient data:\n" + json.dumps(facts, ensure_ascii=False)
        text = self.llm.complete(system=CLINICAL_IMPRESSION_SYSTEM, user=user)
        return text.strip()

    def render_text(self, report: HandoffReport) -> str:
        """Render the 🚨 PATIENT HANDOFF text block."""
        p = report.patient
        lines = [
            "PATIENT HANDOFF - MediCase Orchestrator",
            "",
            f"Case ID:        {report.case_id}",
            f"Name:           {_or_unknown(p.name)}",
            f"Approx. Age:    {_or_unknown(p.approx_age)}",
            f"Sex:            {_or_unknown(p.sex)}",
            f"Language:       {_or_unknown(p.language_name)}",
            f"Location:       {_or_unknown(report.location)}",
            f"Time (UTC):     {report.created_at.isoformat(timespec='seconds')}",
            "",
            f"SYMPTOMS:       {_or_unknown(p.symptoms)}",
            f"PAIN:           {_or_unknown(p.pain_location)} "
            f"({_or_unknown(p.pain_scale, 'n/a')}/10)",
            f"ALLERGIES:      {_or_unknown(p.allergies)}",
            f"MEDICATIONS:    {_or_unknown(p.medications)}",
            f"CHRONIC:        {_or_unknown(p.chronic_conditions)}",
        ]
        if p.wearable_snapshot:
            wear = ", ".join(f"{k}={v}" for k, v in p.wearable_snapshot.items())
            lines.append(f"WEARABLE:       {wear}")
        lines += [
            "",
            f"NEAREST AED:    {_or_unknown(report.nearest_aed)}",
            f"AMBULANCE ETA:  {_or_unknown(report.ambulance_eta_min, 'n/a')} min",
        ]
        if report.drug_warnings:
            lines.append(f"DRUG WARNINGS:  {_or_unknown(report.drug_warnings)}")
        lines += [
            "",
            f"Handed off by:  {_or_unknown(report.handed_off_by)}",
            f"Accepted by:    {_or_unknown(report.accepted_by)}",
        ]
        if report.clinical_impression:
            lines += [
                "",
                f"AI IMPRESSION (not a diagnosis): {report.clinical_impression}",
            ]
        return "\n".join(lines)
