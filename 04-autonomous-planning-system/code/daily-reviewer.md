# Daily Reviewer Agent

**Schedule:** weekday mornings (cloud cron).
**Reads:** priorities/context doc, the active weekly plan, yesterday's signals across all tools.
**Writes:** a daily-update file; every proposed change is an approval checkbox.

## The verification step (the key feature)

For each of yesterday's task blocks, do NOT ask the human whether it was done. Check the evidence and assign a status:

| Status | Evidence required |
|---|---|
| **Verified Complete** | A concrete artifact: a commit, a sent message, a file modified at a specific time by the user |
| **Likely Complete** | Partial or indirect evidence |
| **Unverified** | No trace found — flag it; the human finishes it or formally drops it |

Also check: commitments made yesterday ("I'll send X by EOD" — did it ship?), inbound asks (did the human reply?), and meetings attended.

## Output structure

1. **Summary** — what got done, what's at risk today, key shifts proposed.
2. **Yesterday recap** — the verification table above, plus commitments / inbound asks / meetings.
3. **Context pulled** — audit trail of sources.
4. **Today, revised** — hour-by-hour blocks marked NEW / MOVED / EXISTING / REMOVED, each tied to a context principle.
5. **Rest-of-week ripple** — cascading impact of today's changes.
6. **Approval** — meetings to create, blocks to add, blocks to modify/remove (all checkboxes).
7. **Notes (not actioned)** — risks, observations, pattern detection.

## Why verification matters

Relying on memory for "what did I ship yesterday" is unreliable and lets commitments quietly slip. Confirming completion against real artifacts is a stronger signal and catches dropped balls before they become problems. This is the feature that makes the system trustworthy rather than just another planner.
