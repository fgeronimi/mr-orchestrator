# mr-orchestrator

Mes adaptations pour travailler avec des agents Claude Code pilotés par tickets GitHub, suivis dans [cmux](https://github.com/manaflow-ai/cmux). On part des [skills de Matt Pocock](https://github.com/mattpocock/skills), forkés ici sous le préfixe `mro-` pour les améliorer au fil des rétros, et on n'écrit que ce qui manque.

## Nos skills

| Skill | Rôle |
| --- | --- |
| `mro-setup` | Configure un repo projet : cycle de vie `status:*`, DoR, modèles par rôle, grille de l'arbitre, rejeu. À lancer après `/mro-setup-base`. |
| `mro-arbitrate-pr` | Applique la grille de l'arbitre à une PR : auto-merge ou revue humaine. |
| `mro-sync-skill-forks` | Crée nos forks de skills et les met à jour quand l'original change (fusion à 3 versions). |

## Forks des skills de Matt

Chaque fork a un `UPSTREAM.yaml` (commit d'alignement) et la licence MIT d'origine.

| Rôle | Skills |
| --- | --- |
| Setup | `mro-setup-base` (ex-`setup-matt-pocock-skills`) |
| PO | `mro-grill-with-docs`, `mro-to-spec`, `mro-to-tickets`, `mro-triage` |
| Architecte | `mro-domain-modeling`, `mro-codebase-design`, `mro-wayfinder` |
| Dev | `mro-implement`, `mro-tdd`, `mro-diagnosing-bugs`, `mro-pr` |
| QA | `mro-code-review` |
| Rétro | `mro-retro` |
| Passage de relais | `mro-handoff` |

Renvois laissés vers des skills de Matt non forkés : `writing-for-agents` (`mro-retro`), `research` (`mro-wayfinder`), `improve-codebase-architecture` (`mro-setup-base/domain.md`).

## Installer dans un repo projet

```bash
npx skills@latest add fgeronimi/mr-orchestrator -a claude-code
```

Puis, dans Claude Code : `/mro-setup-base`, puis `/mro-setup`. Commiter `.claude/skills/` et `skills-lock.json` : les worktrees des agents en ont besoin.

## Développer

```bash
uv sync
uv run pytest
```
