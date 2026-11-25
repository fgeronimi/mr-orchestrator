# mr-orchestrator

Le repo de mes adaptations pour travailler avec des agents Claude Code pilotés par tickets GitHub : skills, config, backlogs de rejeu, scripts. Ce n'est pas un produit : on réutilise l'existant (surtout les skills de Matt Pocock) et on n'écrit que ce qui manque.

Spec : `docs/brief.md`. Reprise de contexte : `docs/handoff.md`.

## Organisation

- `skills/<nom>/SKILL.md` : nos skills, installables ailleurs avec `npx skills@latest add fgeronimi/mr-orchestrator`.
- `skills/<nom>/UPSTREAM.yaml` : présent seulement sur un fork ; géré par `/sync-skill-forks`.
- `config/agents.yaml` : modèle par rôle (alias `opus`, `sonnet`, `haiku`, jamais une version).
- `backlogs/*.yaml` : faux tickets pour les rejeux.
- `tests/` : tests des scripts des skills.

## Règles

1. Avant d'écrire un skill, chercher un équivalent chez Matt Pocock (`mattpocock/skills`). Ordre : utiliser tel quel, puis configurer (`docs/agents/*.md`), puis forker. Écrire de zéro en dernier.
2. Un skill installé ne se modifie jamais à la main : on forke ici avec `/sync-skill-forks`.
3. Écrire les skills selon le skill `writing-for-agents` de Matt : courts, une seule responsabilité.
4. Les scripts d'un skill vivent dans `skills/<nom>/scripts/`, n'utilisent que la stdlib et `pyyaml` (métadonnées PEP 723), et ont leurs tests dans `tests/`.
5. Aucune décision de merge n'est prise par un modèle : la grille de l'arbitre est un script.

## Commandes

- `uv sync` : installer
- `uv run pytest` : tests
