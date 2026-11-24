# mr-orchestrator

Orchestrateur générique d'agents Claude Code pilotés par tickets GitHub : Kanban web, sync GitHub, serveur MCP, lancement des agents dans cmux, rejeu de runs.

La spec complète est dans `docs/brief.md`. Lis-la avant toute tâche.

## Règles

- GitHub est la source de vérité. Le statut d'un ticket = son label `status:*`. Ne jamais stocker un statut ailleurs sans le refléter dans GitHub.
- Ce repo est générique : rien de spécifique à `memento` ou `kosmos` dans le code. Ce qui dépend d'un projet va dans `config/` ou `backlogs/`.
- Aucun ticket ne passe en `status:ready` sans validation humaine (validation 1).
- Les modèles se lisent dans `config/agents.yaml`, avec des alias (`opus`, `sonnet`, `haiku`), jamais un identifiant de version en dur.

## Stack

- Python 3.12+, `uv`.
- FastAPI + HTMX + SQLite pour le Kanban, SSE pour le temps réel.
- `gh` / API GitHub pour la sync.
- CLI `mro` (point d'entrée `mr_orchestrator.cli:main`).

## Commandes

- `uv sync` : installer
- `uv run pytest` : tests
- `uv run mro --help` : CLI

## Définition de fini

- Tests ajoutés pour tout code ajouté, `uv run pytest` vert.
- Les critères d'acceptation du ticket sont cochés un par un dans la PR.
