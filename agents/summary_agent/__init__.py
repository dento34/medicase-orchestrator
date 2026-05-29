"""SummaryAgent — Stage 3 (Handoff): build the English handoff package.

Deterministic assembly of structured case data into the receiving-hospital
handoff. The critical clinical fields are template-driven (no LLM, no
hallucination risk). The LLM is used ONLY for an optional one-sentence
clinical impression, clearly labelled as AI-generated.
"""
from .agent import SummaryAgent
from .models import HandoffReport, PatientSnapshot

__all__ = ["SummaryAgent", "HandoffReport", "PatientSnapshot"]
