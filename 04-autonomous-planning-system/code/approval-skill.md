# Approval Skill (Human-in-the-Loop Execution)

The gate between proposal and action. The agents never create anything directly; this skill does, and only for items a human has explicitly checked.

## Flow

1. Find the latest plan or daily-update file.
2. Scan for checked items (`- [x]`).
3. Classify each by the section header above it: meeting to create, task block to add, block to modify/remove, or other action.
4. Execute via the connected tools (calendar, messaging, file edits).
5. Append an entry to an approval log — a permanent audit trail of what ran and when.

If nothing is checked, it does nothing and reports what *would* have run.

## Why this design

The split between "agent proposes" and "human approves" is deliberate. The agent does the heavy synthesis; the human keeps judgment and control. Nothing reaches the real calendar or sends a real message without an explicit check. The audit log means every automated action is traceable after the fact. This is what makes an autonomous system safe to actually run.
