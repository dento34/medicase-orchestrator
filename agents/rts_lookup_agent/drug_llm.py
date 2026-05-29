"""LLM-based drug interaction analysis.

NIH retired the public RxNav `/interaction/*` endpoints in 2024, so we use
an LLM to flag clinically significant interactions. RxCUI resolution (from
`drug.py`) still runs first — it normalizes free-text drug names and gives
us canonical identifiers we can cite.

The LLM is instructed to be conservative: hedge, never invent, and never
recommend dosages. Output is structured DrugInteraction objects.
"""
from __future__ import annotations

import json
import re

from .models import DrugInteraction
from ..shared.llm import LLMClient
from ..shared.logging import get_logger

logger = get_logger("drug_llm")


DRUG_INTERACTION_SYSTEM = """\
You are a clinical pharmacology assistant supporting an emergency medical
triage. Given a list of drugs a patient is taking or may be given, identify
clinically significant pairwise interactions.

Rules:
- Only report interactions you are confident are well-established.
- Use hedged, factual descriptions. Never recommend a dose.
- Severity must be one of: "high", "moderate", "low".
- If there are no significant interactions, return an empty list.

Respond ONLY with a JSON object on a single line, no prose, no code fences:
{"interactions": [{"drug_a": "...", "drug_b": "...", "severity": "high|moderate|low", "description": "..."}]}
"""

_CODE_FENCE_RE = re.compile(r"^```[a-zA-Z0-9_]*\s*|\s*```$", flags=re.MULTILINE)


def _parse_json(text: str) -> dict:
    text = text.strip()
    if text.startswith("```"):
        text = _CODE_FENCE_RE.sub("", text).strip()
    if "{" in text and "}" in text:
        text = text[text.index("{") : text.rindex("}") + 1]
    return json.loads(text)


def check_interactions_llm(
    drug_names: list[str],
    llm: LLMClient,
    *,
    patient_conditions: list[str] | None = None,
) -> list[DrugInteraction]:
    """Ask the LLM for clinically significant interactions among `drug_names`.

    `patient_conditions` (e.g. ['hypertension']) sharpens the analysis.
    Returns a list of DrugInteraction; empty if none or on parse failure.
    """
    drugs = [d for d in dict.fromkeys(drug_names) if d.strip()]
    if len(drugs) < 2:
        return []

    context = ""
    if patient_conditions:
        context = f"\nPatient chronic conditions: {', '.join(patient_conditions)}"
    user = f"Drugs: {', '.join(drugs)}{context}"

    try:
        resp = llm.complete(system=DRUG_INTERACTION_SYSTEM, user=user)
        data = _parse_json(resp)
    except Exception as e:
        logger.warning(f"LLM drug interaction analysis failed: {e}")
        return []

    interactions: list[DrugInteraction] = []
    for item in data.get("interactions", []):
        severity = str(item.get("severity", "n/a")).lower()
        if severity not in {"high", "moderate", "low"}:
            severity = "n/a"
        interactions.append(
            DrugInteraction(
                drug_a=item.get("drug_a", ""),
                drug_b=item.get("drug_b", ""),
                severity=severity,
                description=item.get("description", ""),
                source="LLM",
            )
        )
    logger.info(f"LLM reported {len(interactions)} interaction(s)")
    return interactions
