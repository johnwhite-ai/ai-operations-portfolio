"""Render the sourced profile to a markdown report.

The report is the product. Every value appears with its confidence tag and its
source citation, and the gaps are listed up front as the next questions to ask
the customer. A reader can audit any number in seconds.
"""
from __future__ import annotations

from .confidence import Confidence, assign_confidence, summarize
from .models import Profile


def render(profile: Profile, required: list[str]) -> str:
    counts = summarize(profile.values)
    missing = profile.required_missing(required)

    lines = [
        f"# Solution Inputs & Assumptions — {profile.engagement}",
        "",
        f"**Confirmed:** {counts['Confirmed']} · "
        f"**Estimated:** {counts['Estimated']} · "
        f"**Missing (required):** {len(missing)}",
        "",
        "| Parameter | Value | Confidence | Source |",
        "|---|---|---|---|",
    ]
    for v in profile.values:
        conf = assign_confidence(v).value
        val = f"{v.normalized} {v.unit}" if v.normalized is not None else (v.raw or "—")
        cite = v.source.location + (f" — \"{v.source.excerpt}\"" if v.source.excerpt else "")
        note = f"  _({v.note})_" if v.note else ""
        lines.append(f"| {v.parameter} | {val} | **{conf}** | {cite}{note} |")

    lines += ["", "## Gaps — next questions for the customer", ""]
    if missing:
        for p in missing:
            lines.append(f"- [ ] {p} — not found in any source")
    else:
        lines.append("All required parameters present.")
    return "\n".join(lines)
