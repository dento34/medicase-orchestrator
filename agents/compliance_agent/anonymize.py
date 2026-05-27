"""PII anonymization helpers.

Keep clinical signal, lose identifiers. Bucketed transforms only — no
"randomized noise" tricks, because someone has to be able to verify the
anonymization rules in an audit.
"""
from __future__ import annotations

import hashlib

LANGUAGE_FAMILIES = {
    # Indo-European
    "en": "indo-european",
    "es": "indo-european",
    "pt": "indo-european",
    "fr": "indo-european",
    "it": "indo-european",
    "de": "indo-european",
    "nl": "indo-european",
    "ru": "indo-european",
    "hi": "indo-european",
    # Afro-Asiatic
    "ar": "afro-asiatic",
    "ary": "afro-asiatic",
    "he": "afro-asiatic",
    # Sino-Tibetan
    "zh": "sino-tibetan",
    # Japonic / Koreanic
    "ja": "japonic",
    "ko": "koreanic",
    # Turkic
    "tr": "turkic",
    # Niger-Congo
    "wo": "niger-congo",
    "sw": "niger-congo",
}


def hash_case_id(case_id: str) -> str:
    """Truncated SHA-256 — one-way, stable, short enough to be usable."""
    return hashlib.sha256(case_id.encode("utf-8")).hexdigest()[:16]


def bucket_age(age: int | None) -> str | None:
    if age is None:
        return None
    if age < 1:
        return "infant"
    if age < 13:
        return "child"
    if age < 18:
        return "adolescent"
    if age < 30:
        return "18-29"
    if age < 45:
        return "30-44"
    if age < 60:
        return "45-59"
    if age < 75:
        return "60-74"
    return "75+"


def language_family(language_code: str | None) -> str | None:
    if not language_code:
        return None
    return LANGUAGE_FAMILIES.get(language_code.lower().split("-")[0], "other")
