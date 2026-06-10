"""Map messy source columns to canonical parameters.

This is the AI-assisted edge. Customer exports never use the names the solution
needs ("Dly Ord Qty", "orders / day", "OrderVolume_24h" all mean the same
thing). A deterministic alias table handles the common cases; an AI fuzzy
matcher handles the rest. The AI's suggestion is ALWAYS checked against the
canonical schema before it is accepted — the AI proposes, the rules dispose.
"""
from __future__ import annotations

# Deterministic alias table: known header variants -> canonical parameter.
ALIASES: dict[str, str] = {
    "dly ord qty": "daily_order_volume",
    "orders/day": "daily_order_volume",
    "ordervolume_24h": "daily_order_volume",
    "lines per order": "avg_lines_per_order",
    "lpo": "avg_lines_per_order",
    "sku count": "sku_count",
    "active skus": "sku_count",
    "units per line": "units_per_line",
}

CANONICAL_PARAMETERS = {
    "daily_order_volume", "avg_lines_per_order", "sku_count",
    "units_per_line", "peak_factor", "shift_hours",
}


def match_header(header: str) -> str | None:
    """Deterministic first: exact alias match on a normalized header."""
    key = header.strip().lower()
    return ALIASES.get(key)


def ai_fuzzy_match(header: str, ai_call) -> str | None:
    """AI edge: ask the model to map an unknown header to a canonical parameter.

    The model's answer is only accepted if it is a real canonical parameter.
    A hallucinated parameter name is rejected. The AI never gets to invent a
    field — it can only select from the known schema.
    """
    suggestion = ai_call(
        f"Map the column header '{header}' to one of: "
        f"{sorted(CANONICAL_PARAMETERS)}. Reply with exactly one, or NONE."
    ).strip()
    return suggestion if suggestion in CANONICAL_PARAMETERS else None


def resolve_header(header: str, ai_call=None) -> str | None:
    """Deterministic match first; fall back to checked AI match only if needed."""
    return match_header(header) or (ai_fuzzy_match(header, ai_call) if ai_call else None)
