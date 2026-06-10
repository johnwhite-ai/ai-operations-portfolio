# Example Run

A worked example showing the system route a request, hit a capability gap, and grow to fill it. Illustrative.

## Request

> "Profile this new account's raw operations data and tell me the three biggest risks. They sent a PDF export I've never seen the format of."

## How it flows

**Orchestrator** interprets intent: profile raw data → assess risk → deliver sourced summary. Routes to Operations.

**Operations / data-profiler** starts profiling, but the data is in a PDF table format no current agent can parse. It reports a **capability gap**: "no agent can extract tabular data from this PDF layout."

**Capability Gap Protocol fires:**
1. Orchestrator states the gap.
2. `opportunity-scout` searches and finds an open-source PDF-table-extraction tool.
3. Evaluates: usable as-is with a thin wrapper. Cheaper than building from scratch.
4. A new `pdf-table-extractor` agent is created wrapping the tool.
5. `data-manager` registers it in the CATALOG.

**Work resumes** with the new capability. data-profiler returns a clean, sourced input set (every field Confirmed / Estimated / Missing).

**Production / deliverable-builder** assembles the final summary:

> **Top 3 Risks — New Account**
> 1. Order volume exceeds current capacity by ~20%. *(Estimated — based on confirmed daily volume and stated capacity)*
> 2. SKU count not provided. *(Missing — needed for slotting risk; flagged)*
> 3. Seasonal peak is 3x baseline. *(Confirmed — from the data)*

**Knowledge & Memory** captures the lesson: this account's data format is now known, and the new extractor is available for next time.

## The point

The system did not fail when it hit an unknown format. It recognized the gap, acquired the capability, finished the job, and is now permanently better at it. That is the difference between an automation and a system that grows.
