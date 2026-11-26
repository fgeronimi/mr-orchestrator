# Test de kandev : protocole

Ce qu'on teste : [kandev](https://github.com/kdlbs/kandev) suffit-il pour piloter des agents Claude Code comme une équipe sur memento ? On voit où en est chaque ticket, on ne valide que ce qui compte. On n'écrit pas de code : on configure kandev tel qu'il est livré, et tout ce qui coince va dans `docs/journal.md`.

## Critères

Éliminatoires : un échec arrête le test.

1. **Abonnement** : Claude Code tourne dans kandev avec le `claude login` de l'utilisateur, sans `ANTHROPIC_API_KEY`.
2. **Vue d'ensemble** : un seul écran montre l'étape de chaque ticket, l'agent qui le tient et ce qui attend l'humain.
3. **Validations qui tiennent** : un agent ne peut pas franchir lui-même une transition manuelle, ni merger. La doc kandev dit qu'« Allow manual move » est une règle d'interface, pas une frontière de sécurité, et les agents disposent de `mcp_move` : c'est ce qu'on vérifie.

Notés 0, 1 ou 2 :

4. **Lien GitHub** : import des issues (Issue Watch), lien vers la PR, et mise à jour de l'issue (statut, commentaire, fermeture). La doc ne mentionne pas ce dernier point.
5. **Parallélisme** : tickets 1 et 6 en même temps, dans des worktrees, sans conflit.
6. **Piège** : le ticket 15 est arrêté avant Work.
7. **Coût et suivi** : tokens ou durée visibles par tâche ; part du quota consommée par le run.
8. **Friction** : temps d'installation et de configuration, nombre de sorties de kandev pour débloquer quelque chose.

Verdict : on garde (éliminatoires OK, total ≥ 8/10), on garde avec contournements (éliminatoires OK, total < 8), on arrête (un éliminatoire en échec).

## Configuration cible

- **Workflow** : modèle intégré Feature Dev, tel quel. Todo → Spec → Work → Review → QA → PR → CI Fixup → Done.
- **Profils** : opus en Spec, sonnet pour Work, Review, QA, PR et CI Fixup.
- **Transitions** : manuelles partout. Spec → Work vaut validation de la DoR et du plan ; PR → Done, après ton merge, vaut validation de la PR.
- **Import** : Issue Watch sur memento, filtre label `kandev`, arrivée en Todo (pas en Spec, sinon l'agent démarre avant que tu aies vu le ticket).
- **Branche** : PR vers `main` de memento, tag `kandev-run-000-start` posé avant le run.
- **Skills** : le plugin de Matt seul (global). Aucun skill installé dans memento.

## Étapes

0. **Préparer.** Ce repo devient le carnet de test. Dans memento : retirer `.claude/skills/`, `skills-lock.json` et `docs/agents/triage-labels.md` ; supprimer les labels de triage sur GitHub ; créer le label `kandev`.
1. **Installer.** `brew install kdlbs/kandev/kandev`, lancer `kandev`, ajouter memento. Chronométrer (critère 8).
2. **Abonnement (critère 1).** Tâche jetable dans le workflow Kanban par défaut : « résume le README ». Vérifier qu'elle tourne sans clé API. Échec : on s'arrête.
3. **Validation (critère 3).** Tâche jetable dans Feature Dev, avec un prompt qui pousse l'agent à aller lui-même jusqu'à Done. Si `mcp_move` le laisse passer : chercher un contournement (couper l'outil pour l'agent) et le noter, sinon on s'arrête. Supprimer la tâche et sa branche ensuite.
4. **Configurer.** Feature Dev, profils, Issue Watch.
5. **Lancer `run-000`.** Tag, création des issues 1, 6 et 15 (`backlogs/run-000.yaml`), puis avancer les tickets. Noter au fil de l'eau les critères 2, 4, 5, 6 et 7.
6. **Conclure.** Verdict dans `docs/journal.md`, export du workflow dans `kandev/workflow.yaml`.

Hors de ce tour : kosmos et le multi-repo (tickets 10 et 17 de demo-17), si le verdict le justifie.
