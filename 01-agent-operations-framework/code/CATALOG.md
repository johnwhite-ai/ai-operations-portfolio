# Agent Catalog

The master registry of every agent, organized by department. The orchestrator uses this catalog to route work, and the Capability Gap Protocol updates it when a new agent is acquired.

## Org chart

```
                         ORCHESTRATOR  (executive function)
                              |
   ----------------------------------------------------------------
   |               |              |              |                 |
 Research &     Operations    Production    Administration    Knowledge
 Discovery                                                    & Memory
   |               |              |              |                 |
 3 agents        3 agents      2 agents       2 agents         2 agents
```

## Research & Discovery
*Finds information, qualifies opportunities, and scouts for new capabilities.*

| Agent | Role |
|---|---|
| `market-researcher` | Researches markets, options, and external context |
| `opportunity-scout` | Sizes opportunities AND scouts open-source agents/tools to fill capability gaps |
| `strategy-advisor` | Recommends an approach given the findings |

## Operations
*Researches subjects, profiles raw data, and drives work forward.*

| Agent | Role |
|---|---|
| `subject-researcher` | Deep research on a specific entity or topic |
| `data-profiler` | Turns messy raw data into structured, sourced inputs |
| `engagement-manager` | Tracks the work and drives next steps |

## Production
*Designs the solution and builds the deliverable.*

| Agent | Role |
|---|---|
| `solution-architect` | Designs the solution from requirements, first-principles |
| `deliverable-builder` | Assembles the final, sourced output |

## Administration
*Keeps the system's logistics and data clean.*

| Agent | Role |
|---|---|
| `scheduler` | Coordinates timing and sequencing |
| `data-manager` | Maintains data hygiene; owns this catalog |

## Knowledge & Memory
*The institutional memory that makes the system learn.*

| Agent | Role |
|---|---|
| `knowledge-curator` | Captures reusable knowledge and best practices |
| `memory-keeper` | Recalls history and context from past runs |

## Design philosophy

1. **Specialization beats generalization** — each agent does one thing excellently.
2. **Structure mirrors a proven model** — real companies are organized this way for a reason.
3. **The system learns** — Knowledge & Memory captures lessons; the catalog evolves.
4. **Capability gaps trigger growth** — the system builds what it lacks (Capability Gap Protocol).
5. **Everything is sourced** — no claim without provenance.

*Maintained by the Administration team's `data-manager`. New agents acquired via the Capability Gap Protocol are registered here automatically.*
