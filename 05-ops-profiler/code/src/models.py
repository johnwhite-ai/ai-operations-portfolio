"""Typed data models for the profiler.

Every value that enters a profile carries its provenance and the metadata
needed to assign confidence. There are no orphan numbers — a value cannot
exist in the system without a source attached.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class SourceKind(str, Enum):
    """Where a value originated. Confidence is derived from this."""
    CUSTOMER_STATED = "customer_stated"        # said on a call / in writing
    CUSTOMER_DOCUMENT = "customer_document"     # a deck, PDF, or spec they provided
    SYSTEM_EXPORT = "system_export"             # a raw export from their system
    UNSTRUCTURED_TEXT = "unstructured_text"     # pasted notes, email body
    DERIVED = "derived"                         # computed from other values
    UNKNOWN = "unknown"


@dataclass(frozen=True)
class Source:
    """A pointer back to exactly where a value came from."""
    kind: SourceKind
    location: str           # e.g. "orders.xlsx!Sheet1!C14" or "kickoff call 2026-05-02"
    excerpt: Optional[str] = None   # the literal text/cell, for the citation


@dataclass
class ExtractedValue:
    """A single operational parameter with full provenance."""
    parameter: str                  # canonical name, e.g. "daily_order_volume"
    raw: Optional[str]              # the value as found (None = missing)
    normalized: Optional[float] = None   # canonical-unit value
    unit: Optional[str] = None
    source: Source = field(default_factory=lambda: Source(SourceKind.UNKNOWN, "n/a"))
    derived: bool = False           # computed rather than observed
    ai_extracted: bool = False      # pulled from unstructured text by the AI edge
    note: Optional[str] = None      # assumption made, conflict resolved, etc.


@dataclass
class Profile:
    """The assembled, sourced profile for one engagement."""
    engagement: str
    values: list[ExtractedValue] = field(default_factory=list)

    def required_missing(self, required: list[str]) -> list[str]:
        present = {v.parameter for v in self.values if v.raw is not None}
        return [p for p in required if p not in present]
