# Reprise de contexte

Colle le bloc ci-dessous comme premier message d'une session Claude Code ouverte dans `~/Dev/perso/mr-orchestrator`.

```text
On reprend le projet mr-orchestrator. Lis d'abord CLAUDE.md, docs/brief.md et README.md, puis résume-moi en 5 lignes où on en est avant de faire quoi que ce soit.

Contexte : je teste une méthode de travail avec des agents Claude Code pilotés par tickets GitHub, que je suis dans cmux, avec une posture de PO et de CTO senior. Le but est d'apprendre en assemblant et en adaptant des outils existants, pas de construire un outil nouveau. Ce repo contient mes adaptations (skills, config, backlogs, scripts) ; memento (RAG sur les Pensées de Marc Aurèle) et kosmos (carte des pensées) sont le projet test, dans ~/Dev/perso, avec un tag baseline-v0.

Décisions prises :
- Réutiliser au maximum les skills de Matt Pocock (mattpocock/skills). Ordre : utiliser tel quel, configurer via docs/agents/*.md, forker, écrire de zéro en dernier. Pas d'ai-factory, pas d'aif-handoff, pas de Claude Ship (pas dans mon offre), pas de Kanban fait maison.
- Nos skills : setup-mr-orchestrator (même mécanisme que setup-matt-pocock-skills), arbitrate-pr (grille calculée par skills/arbitrate-pr/scripts/grid.py), sync-skill-forks (forks avec UPSTREAM.yaml, fusion à 3 versions).
- Cycle de vie par labels status:* ; seul l'humain passe un ticket de status:dor-review à status:ready. Quatre validations humaines : DoR, plan, PR si merge:human, rétro.
- Modèles par rôle dans config/agents.yaml : PO et architecte opus, dev/QA/rétro sonnet, arbitre haiku.
- Repos sur mon GitHub perso (fgeronimi).

Prochaine étape :
1. Vérifie que uv run pytest passe, puis aide-moi à pousser ce repo.
2. Dans memento : installer les skills de Matt et les nôtres (npx skills@latest add …), puis lancer /setup-matt-pocock-skills et /setup-mr-orchestrator. Même chose dans kosmos.
3. Ensuite : tester kandev sur backlogs/run-000.yaml (tickets 1, 6, 15 de demo-17).

Règles : ne modifie jamais un skill installé à la main, forke-le avec /sync-skill-forks. Pose-moi une question à la fois quand une décision m'appartient.
```
