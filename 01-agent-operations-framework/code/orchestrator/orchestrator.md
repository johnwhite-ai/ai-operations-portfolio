# Orchestrator

The orchestrator is the executive function of the system. It interprets a request, routes work to the right specialist team, and synthesizes the result. It does not do specialist work itself. It coordinates.

## Mental model: a company, not a toolbox

Most agent systems are a flat pile of tools. This one is modeled on how a real, high-performing company is organized: five departments, each with specialists who are excellent at one function, coordinated by an executive. That structure is what makes the system scalable and the output consistent.

## Routing logic

1. **Interpret intent** — what does the request actually need?
2. **Identify the team(s)** — which department owns this work?
3. **Sequence** — order the tasks and their dependencies.
4. **Delegate** — hand off with clear context and success criteria.
5. **Synthesize** — integrate team outputs into one coherent deliverable.

## Standards enforced on every output

- **Sourced** — every key field tagged Confirmed / Estimated / Missing.
- **First-principles** — derived from the actual situation, not a template.
- **Decision-useful** — helps the user decide or act.
- **Honest about gaps** — missing information is flagged, never hidden.

## The Capability Gap Protocol

When a request needs a capability no current agent provides, the system does not fail. It grows.

1. **Recognize the gap** — state plainly what capability is missing.
2. **Dispatch discovery** — send the Research & Discovery team to find existing open-source agents or tools that fill it.
3. **Evaluate** — use as-is, adapt, or build from scratch.
4. **Build or adapt** — create the new agent in the standard file structure.
5. **Register** — add it to the CATALOG so the capability persists for every future request.

This is what makes the system self-extending. It does not stay static; when it hits a wall, it acquires the missing capability and remembers it. See [`docs/capability-gap-protocol.md`](../../docs/capability-gap-protocol.md).

## Self-improvement loop

After each significant run, Knowledge & Memory captures what worked and what didn't, underperforming agents are flagged for refinement, and the CATALOG stays current. The system improves with use instead of decaying.
