# mr-orchestrator

Carnet de test de [kandev](https://github.com/kdlbs/kandev) pour piloter des agents Claude Code sur le projet test memento. Pas de code : protocole, backlogs, journal, export de la config kandev. On teste l'existant tel quel ; ce qui coince se note, ça ne se contourne pas en écrivant un outil.

Spec : `docs/brief.md`. Protocole : `docs/kandev-test.md`. Observations et verdict : `docs/journal.md`.

## Organisation

- `backlogs/demo-17.yaml` : 17 besoins bruts, dont 3 pièges. `backlogs/run-000.yaml` : les 3 tickets du premier tour.
- `kandev/workflow.yaml` : export du workflow kandev testé (à la fin du tour).

## Règles

1. Rien à construire avant le verdict. Une limite de kandev se note dans le journal avec son contournement éventuel.
2. Skills : le plugin de Matt Pocock seul, en global. Aucun skill installé dans memento pendant le test.
3. Les agents ne passent jamais un ticket au-delà d'une transition manuelle et ne mergent jamais : si kandev le permet, c'est un échec du critère 3, à noter.
