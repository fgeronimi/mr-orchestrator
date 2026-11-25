---
name: mro-setup
description: Configure a project repo for the mr-orchestrator workflow (ticket lifecycle labels, DoR, models per role, arbiter grid, replay baseline). Run once per repo, after /mro-setup-base.
disable-model-invocation: true
---

# mro-setup

Même principe que `/mro-setup-base` : tu explores le repo, tu proposes une réponse recommandée pour chaque choix, l'utilisateur confirme, puis tu écris des fichiers de config que les autres skills relisent. Rien n'est écrit avant confirmation. Relancer ce skill est sans risque : il met à jour au lieu de dupliquer.

Les modèles de fichiers sont dans `templates/` à côté de ce fichier.

## 1. Explorer

- Remote git : GitHub attendu (`gh repo view` doit marcher). Sinon, arrête-toi et dis ce qui manque.
- `CLAUDE.md` ou `AGENTS.md`, et son bloc `## Agent skills`.
- `docs/agents/issue-tracker.md` et `docs/agents/triage-labels.md` : ils prouvent que `/mro-setup-base` a tourné. **S'ils manquent, demande à l'utilisateur de lancer `/mro-setup-base` d'abord**, puis reprends.
- `docs/agents/workflow.md` et `docs/agents/arbiter.yaml` : déjà là = mise à jour, pas création.
- Le langage et l'arborescence (`pyproject.toml`, `package.json`, `src/`, `tests/`, `eval/`), pour proposer les zones sensibles et la commande d'éval.
- Les tags (`git tag`) : `baseline-v0` est le point de départ des rejeux.

## 2. Présenter et demander

Section par section, en commençant par ta recommandation :

**A. Cycle de vie.** Les labels `status:*` de `templates/labels.tsv`. Recommandé : tels quels.

**B. Rôles de triage de Matt.** Ses skills (`mro-triage`, `mro-to-tickets`) parlent en rôles ; on les fait pointer sur nos labels. Recommandé :

| Rôle de Matt | Notre label | Pourquoi |
| --- | --- | --- |
| `needs-triage` | `status:draft` | Le PO affine |
| `needs-info` | `status:needs-info` | Il manque une réponse humaine |
| `ready-for-agent` | `status:dor-review` | Spécifié, mais **la DoR attend ta validation** avant `status:ready` |
| `ready-for-human` | `human-only` | Travail à ne pas confier à un agent |
| `wontfix` | `status:wontfix` | Abandonné |

Seul l'humain passe un ticket de `status:dor-review` à `status:ready` (validation 1). Dis-le explicitement.

**C. Modèles par rôle.** Reprends ceux de `config/agents.yaml` de `mr-orchestrator` (PO et architecte : opus ; dev, QA, rétro : sonnet ; arbitre : haiku). Toujours des alias, jamais une version.

**D. Grille de l'arbitre.** Seuil de diff (150 lignes hors tests), zones sensibles propres à ce repo (par exemple ingestion, embeddings, index pour un RAG), fichiers de dépendances, éval obligatoire ou non.

**E. Rejeu.** Tag de départ (`baseline-v0`) et commande d'éval s'il y en a une (sinon « aucune »).

## 3. Confirmer

Montre les brouillons complets de chaque fichier. L'utilisateur peut tout modifier.

## 4. Écrire

- `docs/agents/workflow.md` depuis `templates/workflow.md`.
- `docs/agents/arbiter.yaml` depuis `templates/arbiter.yaml`.
- `docs/agents/triage-labels.md` : remplace la colonne « Label in our tracker » par le mapping B. Ne touche à rien d'autre dans ce fichier.
- Le bloc `## Agent skills` de `CLAUDE.md` (ou `AGENTS.md`) : ajoute ou mets à jour une sous-section `### Workflow mr-orchestrator`, deux lignes, qui pointent vers `docs/agents/workflow.md` et `docs/agents/arbiter.yaml`. Ne touche pas aux sous-sections de Matt.
- Labels : pour chaque ligne de `templates/labels.tsv`, `gh label create "<nom>" --color <couleur> --description "<description>" --force`.

## 5. Terminer

Dis quels skills lisent ces fichiers : `mro-arbitrate-pr` lit `arbiter.yaml` ; `mro-triage`, `mro-to-tickets` et le PO lisent `triage-labels.md` et `workflow.md`. Pour changer un réglage plus tard, on édite directement `docs/agents/*.md`.
