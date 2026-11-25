---
name: sync-skill-forks
description: Create a fork of an upstream skill, or bring our forks up to date with their upstream (three-way merge, conflicts resolved with the user). Use in the mr-orchestrator repo.
disable-model-invocation: true
---

# Sync skill forks

Nos skills forkés vivent dans `skills/<nom>/` du repo `mr-orchestrator`, chacun avec un `UPSTREAM.yaml` (repo, chemin, branche, commit d'alignement). Ce skill crée un fork ou le remet à jour quand l'original a changé.

Règle d'or : un skill installé (`.claude/skills/`, `.agents/skills/`) ne se modifie jamais à la main. On le configure (fichiers `docs/agents/*.md`) ; si la config ne suffit pas, on le forke ici.

Le script est `scripts/sync_forks.py` dans le dossier de ce skill. Lance-le depuis la racine de `mr-orchestrator` avec `uv run <dossier-du-skill>/scripts/sync_forks.py …`. Il affiche du JSON.

## Ce que l'utilisateur peut demander

- **« Forke `tdd` de Matt »** → `fork mattpocock/skills skills/engineering/tdd tdd`. Trouve le chemin exact dans le repo upstream avant de lancer. Puis rappelle d'ajouter le skill à la table des skills du `README.md`.
- **« Où en sont nos forks ? »** → `check`. Présente un tableau : fork, à jour ou non, fichiers que l'upstream a changés. Ne modifie rien.
- **« Mets les forks à jour »** → déroule la procédure ci-dessous.

## Mettre à jour

1. Vérifie que le working tree est propre (`git status`). Sinon, arrête-toi et demande.
2. `check`, puis montre à l'utilisateur, fork par fork, ce que l'upstream a changé : lis le diff upstream entre `commit` et `latest` dans le cache (`~/.cache/mr-orchestrator/upstream/<repo>`) et résume-le en une ou deux phrases. Demande quels forks mettre à jour.
3. `update <nom>` pour chaque fork retenu. Le script :
   - prend l'upstream pour les fichiers qu'on n'a pas touchés ;
   - fusionne avec `git merge-file` ceux que les deux côtés ont modifiés ;
   - garde nos fichiers que l'upstream a supprimés (action `kept-local`) : signale-les ;
   - avance `commit` s'il n'y a pas de conflit, sinon note `pending` et sort avec le code 3.
4. Conflits : pour chaque bloc `<<<<<<< fork … >>>>>>> upstream`, explique les deux versions en une phrase chacune et propose une résolution. **Attends l'accord de l'utilisateur** avant d'écrire. Garde l'intention de notre fork ; reprends les améliorations de l'upstream quand elles ne la contredisent pas.
5. Quand plus aucun marqueur ne reste : `done <nom>`.
6. Résume : forks mis à jour, conflits résolus, `kept-local`. Propose un commit `chore(skills): sync <noms> avec upstream`.

## Skills installés sans fork

Dans un repo projet (`memento`, `kosmos`), les skills installés par `npx skills` sont tracés dans `skills-lock.json` (commit source + hash des fichiers). Pour eux :

- `npx skills@latest check` signale un skill installé modifié à la main : propose de le forker ici, puis de réinstaller l'original.
- `npx skills@latest update` met à jour les skills non forkés.
