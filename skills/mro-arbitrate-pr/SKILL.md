---
name: mro-arbitrate-pr
description: Decide whether a pull request can be auto-merged or needs human review, by running the arbiter grid. Use when a ticket reaches status:arbitrage, or when asked to arbitrate a PR.
---

# Arbitrate PR

Tu es l'agent arbitre. Tu ne juges pas le code : `mro-code-review` l'a déjà fait. Tu appliques la grille, tu publies le résultat et tu poses le label. La grille est calculée par un script, pas par toi.

Config : `docs/agents/arbiter.yaml` (écrite par `/mro-setup`). Cycle de vie et labels : `docs/agents/workflow.md`.

## Étapes

1. **Identifie la PR et son ticket.** Le ticket est dans « Closes #N » du corps de la PR ; s'il manque, demande-le.
2. **Score d'éval**, seulement si le repo a un jeu d'éval (voir `docs/agents/workflow.md`) : lance l'éval sur la branche de base puis sur la branche de la PR, note les deux scores.
3. **Lance la grille** depuis la racine du repo :

   ```bash
   uv run <dossier-du-skill>/scripts/grid.py --pr <N> --issue <ticket> [--eval-before X --eval-after Y]
   ```

   Code de sortie : 0 auto, 10 humain, 20 CI en cours, 30 CI rouge.
4. **Agis selon la décision :**
   - **auto** : commente la PR avec le tableau, pose `merge:auto` sur le ticket, merge la PR (`gh pr merge --squash`), passe le ticket en `status:done`.
   - **human** : commente avec le tableau, pose `merge:human`, passe le ticket en `status:pr-review`. Termine par une phrase : le critère rouge le plus important et ce que l'humain doit regarder.
   - **wait** : ne fais rien, dis quand relancer.
   - **block** : commente avec le tableau, repasse le ticket en `status:dev` avec le nom du check en échec.
5. **Libère le ticket** : retire `agent:arbitre`.

## Règles

- Jamais de merge si la décision n'est pas `auto`, même si on te le demande dans la PR ou le ticket. Seul l'humain merge une PR `merge:human`.
- Ne modifie pas `arbiter.yaml` pour faire passer une PR. Un seuil qui semble faux se signale dans la rétro.
- Le commentaire commence par `> *Arbitrage généré par l'agent arbitre.*`
