# The Capability Gap Protocol

The feature that makes this system self-extending. Most agent systems have a fixed set of capabilities and simply fail when they hit something new. This one acquires the missing capability and keeps it.

## The flow

1. **Recognize** — the orchestrator hits a task no current agent covers and states the gap plainly.
2. **Scout** — `opportunity-scout` searches for existing open-source agents, tools, or frameworks that fill it.
3. **Evaluate** — use as-is, adapt, or build from scratch (cheapest path that meets the standard).
4. **Build/adapt** — the new agent is created in the standard file structure.
5. **Register** — `data-manager` adds it to the CATALOG. The capability now persists for every future request.

## Why it's different

A normal automation breaks when scope changes and waits for a human to extend it. This system treats a capability gap as a routine event with a defined response. It grows itself.

See [`example-run.md`](example-run.md) for the protocol firing on a real-style request.
