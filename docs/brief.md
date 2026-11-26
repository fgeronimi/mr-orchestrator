# MrOrchestrator — brief

Version du 26 novembre 2026. Remplace la version du 25 novembre (workflow fait maison), conservée dans l'historique git.

## Objectif

Tester une méthode de travail avec des agents Claude Code, suivis dans cmux, avec une posture de PO et de CTO senior. On apprend en **assemblant des outils existants**, pas en construisant un outil nouveau.

Le test réussit si je pilote des agents comme une équipe : je vois où en est chaque ticket, je ne valide que ce qui compte. Rejouer un scénario pour comparer des variantes n'est plus un objectif.

## Décisions

| Sujet | Décision |
| --- | --- |
| Orchestration et Kanban | [kandev](https://github.com/kdlbs/kandev), testé tel quel |
| Skills | Plugin de Matt Pocock, en global. Plus de forks `mro-*` |
| Cycle de vie | Celui de kandev, modèle Feature Dev, transitions manuelles |
| Tickets | Issues GitHub de memento, importées par Issue Watch (label `kandev`) |
| Validations humaines | Spec → Work (DoR et plan), PR → Done (revue et merge) |
| Modèles | opus en Spec, sonnet ailleurs |
| Arbitre, auto-merge, rejeux | Abandonnés |
| Ce repo | Carnet de test, sans code. Nom gardé jusqu'au verdict |

Écartés : ai-factory, aif-handoff, Claude Ship, un Kanban ou un visualiseur fait maison, nos skills `mro-*`.

## Les repos

| Repo | Rôle |
| --- | --- |
| `mr-orchestrator` | Protocole, backlogs, journal, export de la config kandev |
| `memento` | Projet test du premier tour : RAG local sur les *Pensées* de Marc Aurèle (trad. Barthélemy-Saint-Hilaire, 1876). Tag `baseline-v0` |
| `kosmos` | Projet test d'un second tour éventuel : carte 2D des pensées |

## Protocole

Voir `docs/kandev-test.md` : 3 critères éliminatoires (abonnement, vue d'ensemble, validations qui tiennent), 5 critères notés, et l'ordre des étapes. Premier tour : `backlogs/run-000.yaml` (tickets 1, 6 et 15 de `demo-17`), dans memento.

## Corpus

Traduction Barthélemy-Saint-Hilaire sur [Wikisource](https://fr.wikisource.org/wiki/Pens%C3%A9es_pour_moi-m%C3%AAme/Livre_VI), livre par livre, pensées en chiffres romains. Piège : les commentaires du traducteur sont mêlés aux pensées. Une pensée = un document `livre.pensée` (`VI.1`). Stack locale sans modèle payant : embeddings multilingues (bge-m3 ou multilingual-e5), index local, BM25, Ollama en option.

## Questions ouvertes

- Le quota Claude Code tient-il plusieurs agents en parallèle sur un run ?
- kandev met-il à jour les issues GitHub, ou seulement les PR ?
- Second tour : kosmos et un ticket multi-repo (10 ou 17), selon le verdict.
- Le nom du repo, au verdict.
