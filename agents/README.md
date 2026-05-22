# Agents

This folder will contain the coded agent implementations (Python SDK).

Each agent gets its own subfolder:

```
agents/
├── language_agent/        # Stage 1 — voice triage, translation
├── rts_lookup_agent/      # Stage 2 — AED, drug, ambulance ETA
├── compliance_agent/      # Stage 4 — audit + learning
├── shared/                # common utilities (case context, logging)
└── requirements.txt       # Python deps
```

Low-code agents (TriageAgent, RoutingAgent) live in UiPath Agent Builder and are exported separately — see [docs/agents.md](../docs/agents.md) for their specs.

To be built during Weeks 3–5 (see [docs/learning-path.md](../docs/learning-path.md)).
