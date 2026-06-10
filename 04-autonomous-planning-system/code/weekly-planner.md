# Weekly Planner Agent

**Schedule:** Fridays, early morning (cloud cron — runs with no machine on).
**Reads:** priorities/context doc, calendar, messages, shared docs, meeting notes.
**Writes:** a weekly-plan file with every proposed action as an approval checkbox.

## Run sequence

1. **Reconcile prep folders** — move prep files between this-week / next-week / archive as time has passed.
2. **Build next week's plan** — synthesize context into the structure below.
3. **Generate prep files** — for each task block, draft a starting-point prep note (purpose, key questions, deliverable).

## Output structure

1. **Summary** — 3–5 sentences: the week's theme, the anchor deliverables, the biggest risk.
2. **Critical context** — table with severity markers; each row is an item and why it matters.
3. **Projects** — per active project: status, deliverables (this week vs later), tasks already scheduled, and recommended tasks not yet scheduled (as checkboxes).
4. **Meetings** — external and internal, with day, time, attendees, purpose.
5. **Task changes** — modifications/removals to existing blocks, and new task adds (checkboxes).
6. **Notes (not actioned)** — risks and observations, no checkboxes.
7. **Context pulled** — audit trail: every source consulted, status (read / partial / failed), takeaway.

## Principle

The single context doc is the control surface. When a run drifts from reality, the fix is to add the missing context, not to edit the agent. "What context would have prevented this?" is the maintenance loop.
