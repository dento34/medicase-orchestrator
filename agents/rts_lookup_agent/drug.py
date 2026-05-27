"""Drug-interaction lookup via NIH RxNav API.

RxNav is free, no key required.
Endpoint: https://rxnav.nlm.nih.gov/REST

NOTE: NIH retired the multi-drug `/interaction/list.json` endpoint in 2024.
The single-drug `/interaction/interaction.json?rxcui=...` endpoint is still
served. We therefore query each drug separately and filter the returned
pairs to those involving another drug in the patient's regimen.

Pipeline:
  1. For each drug name (free text), resolve to an RxCUI via /REST/rxcui.json
  2. For each resolved RxCUI, fetch `/interaction/interaction.json`
  3. Filter the result set down to pairs where BOTH drugs are in our input
"""
from __future__ import annotations

import json
import os
import re
import urllib.parse
import urllib.request

from .models import DrugInteraction
from ..shared.logging import get_logger

logger = get_logger("drug")

DEFAULT_RXNAV_BASE = "https://rxnav.nlm.nih.gov/REST"
_DOSAGE_STRIP_RE = re.compile(r"\s*\b\d+(\.\d+)?\s*(mg|g|mcg|ml|iu)\b.*", re.IGNORECASE)


def _normalize_drug_name(raw: str) -> str:
    """Strip dosage to improve RxNav name->RxCUI match rate."""
    name = _DOSAGE_STRIP_RE.sub("", raw).strip()
    return name


def _http_json(url: str, timeout_s: int = 15) -> dict:
    req = urllib.request.Request(
        url,
        headers={
            "Accept": "application/json",
            "User-Agent": "MediCase-Orchestrator/0.1 (UiPath AgentHack)",
        },
    )
    with urllib.request.urlopen(req, timeout=timeout_s) as resp:
        return json.loads(resp.read().decode("utf-8"))


def name_to_rxcui(name: str, *, base: str | None = None) -> str | None:
    base = base or os.getenv("RXNAV_BASE_URL") or DEFAULT_RXNAV_BASE
    clean = _normalize_drug_name(name)
    if not clean:
        return None
    url = f"{base}/rxcui.json?{urllib.parse.urlencode({'name': clean})}"
    try:
        data = _http_json(url)
    except Exception as e:
        logger.warning(f"name_to_rxcui failed for '{name}': {e}")
        return None
    ids = (data.get("idGroup") or {}).get("rxnormId") or []
    if ids:
        logger.info(f"'{name}' -> rxcui {ids[0]}")
        return ids[0]
    logger.info(f"'{name}' -> no rxcui match")
    return None


def _interactions_for_one(rxcui: str, base: str) -> list[dict]:
    """Fetch the raw interactionPair list for a single RxCUI."""
    url = f"{base}/interaction/interaction.json?rxcui={rxcui}"
    try:
        data = _http_json(url)
    except Exception as e:
        logger.warning(f"RxNav interaction lookup failed for rxcui={rxcui}: {e}")
        return []
    pairs: list[dict] = []
    for grp in (data.get("interactionTypeGroup") or []):
        for itype in grp.get("interactionType") or []:
            for pair in itype.get("interactionPair") or []:
                pairs.append(pair)
    return pairs


def check_interactions(
    drug_names: list[str],
    *,
    base: str | None = None,
) -> list[DrugInteraction]:
    """Look up pairwise interactions for a list of drugs.

    Returns interactions where BOTH drugs are in the input. If a drug can't
    be resolved to an RxCUI it's silently skipped (and a warning logged).
    """
    base = base or os.getenv("RXNAV_BASE_URL") or DEFAULT_RXNAV_BASE
    name_by_rxcui: dict[str, str] = {}
    rxcuis: list[str] = []
    for name in drug_names:
        rxcui = name_to_rxcui(name, base=base)
        if rxcui:
            name_by_rxcui[rxcui] = name
            rxcuis.append(rxcui)

    if len(rxcuis) < 2:
        # Single-drug regimen → no pairwise interactions to compute.
        return []

    rxcui_set = set(rxcuis)
    seen: set[tuple[str, str]] = set()
    interactions: list[DrugInteraction] = []

    for rxcui in rxcuis:
        for pair in _interactions_for_one(rxcui, base):
            concepts = pair.get("interactionConcept") or []
            if len(concepts) < 2:
                continue
            a_rxcui = (
                ((concepts[0].get("minConceptItem") or {}).get("rxcui"))
                or concepts[0].get("rxcui")
            )
            b_rxcui = (
                ((concepts[1].get("minConceptItem") or {}).get("rxcui"))
                or concepts[1].get("rxcui")
            )
            if not a_rxcui or not b_rxcui:
                continue
            # Only keep interactions among the patient's own drugs.
            if a_rxcui not in rxcui_set or b_rxcui not in rxcui_set:
                continue
            key = tuple(sorted([a_rxcui, b_rxcui]))
            if key in seen:
                continue
            seen.add(key)

            severity_str = (pair.get("severity") or "").lower()
            severity = severity_str if severity_str in {
                "high", "moderate", "low",
            } else "n/a"

            interactions.append(
                DrugInteraction(
                    drug_a=name_by_rxcui.get(a_rxcui, str(a_rxcui)),
                    drug_b=name_by_rxcui.get(b_rxcui, str(b_rxcui)),
                    severity=severity,
                    description=pair.get("description") or "",
                    source="RxNav",
                )
            )

    logger.info(
        f"RxNav reported {len(interactions)} pairwise interaction(s) "
        f"for {len(rxcuis)} resolved drug(s)"
    )
    return interactions
