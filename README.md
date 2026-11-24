# mr-orchestrator

Orchestrateur d'agents IA pilotés par tickets : Kanban, sync GitHub, serveur MCP, agents Claude Code lancés dans [cmux](https://github.com/manaflow-ai/cmux).

- Spec : [`docs/brief.md`](docs/brief.md)
- Rôles et modèles : [`config/agents.yaml`](config/agents.yaml)
- Backlogs de rejeu : [`backlogs/`](backlogs/)

Statut : squelette. Le MVP se construit ticket par ticket, avec la méthode qu'il automatisera.

```bash
uv sync
uv run mro --help
uv run pytest
```
