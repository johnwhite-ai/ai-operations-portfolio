"""Assign a confidence level to every extracted value.

The core idea: confidence comes from WHERE a value came from and HOW it was
obtained, never from the value itself. A number the customer stated is
Confirmed; a number we derived or the AI pulled from prose is Estimated; a
required parameter we never found is Missing. This rule lives in one place so
the standard is applied identically every run.
"""
from __future__ import annotations

from enum import Enum

from .models import ExtractedValue, SourceKind


class Confidence(str, Enum):
    CONFIRMED = "Confirmed"
    ESTIMATED = "Estimated"
    MISSING = "Missing"


# Only these source kinds are trustworthy enough to mark a value Confirmed.
_CONFIRMED_SOURCES = {
    SourceKind.CUSTOMER_STATED,
    SourceKind.CUSTOMER_DOCUMENT,
    SourceKind.SYSTEM_EXPORT,
}


def assign_confidence(value: ExtractedValue) -> Confidence:
    """Rule-based confidence assignment.

    Confirmed — came directly from a trustworthy customer source, intact.
    Estimated — derived, inferred, unit-converted from a partial source, or
                AI-extracted from unstructured text and not yet verified.
    Missing   — no value found for a required parameter.
    """
    if value is None or value.raw is None:
        return Confidence.MISSING
    if value.derived or value.ai_extracted:
        return Confidence.ESTIMATED
    if value.source.kind in _CONFIRMED_SOURCES:
        return Confidence.CONFIRMED
    return Confidence.ESTIMATED


def summarize(values: list[ExtractedValue]) -> dict[str, int]:
    """Count values by confidence level for the report header."""
    counts = {c.value: 0 for c in Confidence}
    for v in values:
        counts[assign_confidence(v).value] += 1
    return counts
