# mr-orchestrator

Mes adaptations pour travailler avec des agents Claude Code pilotés par tickets GitHub, suivis dans [cmux](https://github.com/manaflow-ai/cmux). On réutilise au maximum les [skills de Matt Pocock](https://github.com/mattpocock/skills) et on n'écrit que ce qui manque.

## Nos skills

| Skill | Rôle |
| --- | --- |
| `setup-mr-orchestrator` | Configure un repo projet : cycle de vie `status:*`, DoR, modèles par rôle, grille de l'arbitre, rejeu. À lancer après `/setup-matt-pocock-skills`. |
| `arbitrate-pr` | Applique la grille de l'arbitre à une PR : auto-merge ou revue humaine. |
| `sync-skill-forks` | Crée nos forks de skills et les met à jour quand l'original change (fusion à 3 versions). |

## Skills de Matt utilisés

| Rôle | Skills |
| --- | --- |
| PO | `grill-with-docs`, `to-spec`, `to-tickets`, `triage` |
| Architecte | `domain-modeling`, `codebase-design`, `wayfinder` |
| Dev | `implement`, `tdd`, `diagnosing-bugs`, `pr` |
| QA | `code-review` |
| Rétro | `retro` |
| Passage de relais | `handoff` |

## Installer dans un repo projet

```bash
npx skills@latest add mattpocock/skills -a claude-code
npx skills@latest add fgeronimi/mr-orchestrator -a claude-code
```

Puis, dans Claude Code : `/setup-matt-pocock-skills`, puis `/setup-mr-orchestrator`.

## Développer

```bash
uv sync
uv run pytest
```
