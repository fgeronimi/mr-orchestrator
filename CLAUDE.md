# mr-orchestrator

Le repo de mes adaptations pour travailler avec des agents Claude Code pilotés par tickets GitHub : skills, config, backlogs de rejeu, scripts. Ce n'est pas un produit : on part de l'existant (surtout les skills de Matt Pocock), on le forke pour l'améliorer, et on n'écrit que ce qui manque.

Spec : `docs/brief.md`. Reprise de contexte : `docs/handoff.md`.

## Organisation

- `skills/mro-<nom>/SKILL.md` : nos skills, préfixés `mro-`, installables ailleurs avec `npx skills@latest add fgeronimi/mr-orchestrator`.
- `skills/mro-<nom>/UPSTREAM.yaml` : présent seulement sur un fork ; géré par `/mro-sync-skill-forks`.
- `config/agents.yaml` : modèle par rôle (alias `opus`, `sonnet`, `haiku`, jamais une version).
- `backlogs/*.yaml` : faux tickets pour les rejeux.
- `tests/` : tests des scripts des skills.

## Règles

1. Les skills de Matt qu'on utilise sont forkés ici sous le préfixe `mro-`, même tant qu'on ne les a pas modifiés : ce sont les nôtres, on les améliore à chaque rétro. L'original reste suivi par `UPSTREAM.yaml` et `/mro-sync-skill-forks`. Pour un besoin nouveau, chercher d'abord un équivalent chez Matt et le forker ; écrire de zéro en dernier.
2. Un skill installé dans un repo projet ne se modifie jamais à la main : on modifie son fork ici, puis on réinstalle.
3. Écrire les skills selon le skill `writing-for-agents` de Matt : courts, une seule responsabilité.
4. Les scripts d'un skill vivent dans `skills/<nom>/scripts/`, n'utilisent que la stdlib et `pyyaml` (métadonnées PEP 723), et ont leurs tests dans `tests/`.
5. Aucune décision de merge n'est prise par un modèle : la grille de l'arbitre est un script.

## Commandes

- `uv sync` : installer
- `uv run pytest` : tests
