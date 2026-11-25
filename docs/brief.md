# MrOrchestrator — brief

Version du 25 novembre 2026. Le doc vivant : « MrOrchestrator — brief du workflow d'agents IA » (claude.ai). Ce fichier en est la copie de travail pour les agents.

## Objectif

Tester une méthode de travail avec des agents Claude Code pilotés par tickets GitHub, suivis dans cmux, avec une posture de PO et de CTO senior. On apprend en **assemblant et en adaptant des outils existants**, pas en construisant un outil nouveau.

Le test réussit si je pilote des agents comme une équipe : je vois où en est chaque ticket, je ne valide que ce qui compte, et je peux rejouer le même scénario pour comparer des variantes (modèle, prompt, grille, validations).

## Les repos

| Repo | Rôle |
| --- | --- |
| `mr-orchestrator` | Mes adaptations : skills, config, backlogs, scripts. Source de skills installable avec `npx skills`. |
| `memento` | Projet test : RAG local sur les *Pensées* de Marc Aurèle (trad. Barthélemy-Saint-Hilaire, 1876). Tag `baseline-v0`. |
| `kosmos` | Projet test : carte 2D des pensées et dashboard d'éval. Tag `baseline-v0`. |

## Construire ou réutiliser

Règle : utiliser tel quel, puis configurer, puis forker. Écrire de zéro en dernier.

| Brique | Choix |
| --- | --- |
| Skills des rôles PO, architecte, dev, QA, rétro | Skills de Matt Pocock (voir `README.md`) |
| Machine à états des tickets | `triage` de Matt, ses rôles pointés sur nos labels `status:*` par `/setup-mr-orchestrator` |
| Configuration d'un repo projet | `/setup-matt-pocock-skills` puis notre `/setup-mr-orchestrator` (même mécanisme : explorer, proposer, confirmer, écrire `docs/agents/*`) |
| Arbitre de merge | Notre skill `arbitrate-pr` ; la grille est un script (`grid.py`), pas un modèle. Pas de Claude Ship (offre non éligible). |
| Mise à jour des forks de skills | Notre skill `sync-skill-forks` (fusion à 3 versions avec `git merge-file`) |
| Kanban et agents en parallèle | À tester : kandev. Sinon : labels GitHub + workspaces cmux + nos scripts. |
| Rejeu de runs | À construire : script de rejeu depuis `baseline-v0` et `backlogs/*.yaml` |
| Vue des agents dans cmux | À construire : lancement des agents dans des workspaces cmux, hooks Claude Code vers les notifications cmux |

Écartés : ai-factory (on fait nos propres skills), aif-handoff (repose sur ai-factory), un Kanban fait maison.

## Cycle de vie et validations

Référence complète : `skills/setup-mr-orchestrator/templates/workflow.md` (copié dans `docs/agents/workflow.md` de chaque repo projet).

Quatre validations humaines :

1. **DoR** : `status:dor-review` → `status:ready`. Seul l'humain fait ce passage.
2. **Plan** : `status:plan-review` → `status:dev`.
3. **PR** : `status:pr-review`, seulement quand l'arbitre a posé `merge:human`.
4. **Rétro** : synthèse de fin de run (skill `retro` de Matt).

Gabarit DoR : `.github/ISSUE_TEMPLATE/ticket-dor.md`, tous les champs obligatoires.

## Modèles par rôle

`config/agents.yaml` : PO et architecte en opus ; dev, QA, rétro en sonnet ; arbitre en haiku. Surchargeable par variante de run et par ticket (label `model:*`). À confirmer par un run comparatif.

## Grille de l'arbitre

Auto-merge seulement si tout est vert : CI verte, diff ≤ 150 lignes hors tests, aucune zone sensible, aucune dépendance modifiée, score d'éval stable ou en hausse, tests présents pour le code ajouté, un seul repo, `risk:low`. Config par repo : `docs/agents/arbiter.yaml`. Seuils à calibrer avec les rejeux.

## Rejeu

Un run ne touche jamais `main` : il part de `baseline-v0` et merge dans `run/NNN`. Backlogs : `backlogs/demo-17.yaml` (17 besoins, dont 3 pièges) et `backlogs/run-000.yaml` (tickets 1, 6, 15 pour le rodage). Métriques : durée par étape, temps d'attente humaine, tokens et coût par agent et par modèle, allers-retours par validation, part d'auto-merge, désaccords arbitre/humain, rappel@5 et MRR de `memento`.

## Corpus

Traduction Barthélemy-Saint-Hilaire sur [Wikisource](https://fr.wikisource.org/wiki/Pens%C3%A9es_pour_moi-m%C3%AAme/Livre_VI), livre par livre, pensées en chiffres romains. Piège : les commentaires du traducteur sont mêlés aux pensées. Une pensée = un document `livre.pensée` (`VI.1`). Stack locale sans modèle payant : embeddings multilingues (bge-m3 ou multilingual-e5), index local, BM25, Ollama en option. Éval : ~40 questions avec pensées attendues dans `memento/eval/`.

## Prochaines étapes

1. ✅ Créer les 3 repos, labels et tag `baseline-v0`.
2. ✅ Écrire nos skills : `setup-mr-orchestrator`, `arbitrate-pr`, `sync-skill-forks`.
3. Pousser `mr-orchestrator`, puis installer les skills de Matt et les nôtres dans `memento` et `kosmos`, et lancer les deux setups.
4. Essayer kandev sur `run-000` et décider du socle.
5. Écrire le script de rejeu et brancher cmux.
6. Lancer `run-001` sur `demo-17`.

## Questions ouvertes

- Où vivent les tickets multi-repo (10, 17) : dans `memento`, `kosmos`, ou un repo dédié ?
- Le quota Claude Code tient-il 5 agents en parallèle sur un run complet ?
- Seuils de la grille et répartition des modèles : à calibrer au premier run.
- Source libre pour Épictète, si l'on garde la comparaison.
