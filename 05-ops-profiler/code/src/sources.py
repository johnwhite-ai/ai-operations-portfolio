"""Provenance tracking — the spine of the whole tool.

Every extracted value keeps a pointer to exactly where it came from: which
file, which sheet, which cell, or which sentence of pasted text. When a value
is derived from others, its source records the derivation. Nothing enters a
profile without a source, so the report can cite every single number.
"""
from __future__ import annotations

from .models import Source, SourceKind


def from_cell(filename: str, sheet: str, cell: str, excerpt: str | None = None) -> Source:
    return Source(SourceKind.SYSTEM_EXPORT, f"{filename}!{sheet}!{cell}", excerpt)


def from_document(filename: str, locator: str, excerpt: str | None = None) -> Source:
    return Source(SourceKind.CUSTOMER_DOCUMENT, f"{filename}:{locator}", excerpt)


def from_statement(when: str, excerpt: str) -> Source:
    """A value the customer stated verbally or in writing."""
    return Source(SourceKind.CUSTOMER_STATED, when, excerpt)


def from_text(span: str, excerpt: str) -> Source:
    """A value the AI edge pulled from unstructured prose. Always Estimated until verified."""
    return Source(SourceKind.UNSTRUCTURED_TEXT, span, excerpt)


def derived_from(*parents: str) -> Source:
    """A value computed from other parameters; records what it was built from."""
    return Source(SourceKind.DERIVED, "derived(" + ", ".join(parents) + ")")
