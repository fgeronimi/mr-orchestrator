# Workflow mr-orchestrator

Ce repo est piloté par tickets GitHub, traités par des agents Claude Code. Ce fichier est la référence pour tous les agents.

## Cycle de vie

Une étape = un label `status:*`. Un agent prend un ticket en posant son label `agent:*` et le retire quand il a fini.

| Label | Qui fait avancer | Étape suivante |
| --- | --- | --- |
| `status:draft` | Agent PO (`mro-grill-with-docs`, `mro-to-spec`, `mro-to-tickets`) | `status:dor-review` |
| `status:needs-info` | Humain : répondre aux questions du ticket | `status:draft` |
| `status:dor-review` | **Humain, validation 1** | `status:ready` ou retour en `status:draft` |
| `status:ready` | Orchestrateur, dès qu'un slot se libère | `status:planning` |
| `status:planning` | Agent architecte | `status:plan-review` |
| `status:plan-review` | **Humain, validation 2** | `status:dev` ou retour en `status:planning` |
| `status:dev` | Agent dev (`mro-implement`, `mro-tdd`) | `status:qa` |
| `status:qa` | Agent QA (`mro-code-review`) | `status:arbitrage` ou retour en `status:dev` |
| `status:arbitrage` | Agent arbitre (`mro-arbitrate-pr`) | `status:done` ou `status:pr-review` |
| `status:pr-review` | **Humain, validation 3** | `status:done` ou retour en `status:dev` |
| `status:done` | — | — |
| `status:blocked` | N'importe quel agent après 3 échecs | Décision humaine |
| `status:wontfix` | Humain | — |

Un agent ne passe jamais lui-même un ticket en `status:ready`, et ne merge jamais une PR `merge:human`.

## Definition of Ready

Tous les champs du gabarit `.github/ISSUE_TEMPLATE/ticket-dor.md` sont remplis : contexte, critères d'acceptation vérifiables, hors périmètre, dépendances, risque justifié (`risk:*`), repos touchés (`repo:*`).

## Modèles par rôle

| Rôle | Modèle |
| --- | --- |
| PO | {{model_po}} |
| Architecte | {{model_archi}} |
| Dev | {{model_dev}} |
| QA | {{model_qa}} |
| Arbitre | {{model_arbitre}} |
| Rétro | {{model_retro}} |

Un label `model:*` sur le ticket remplace le modèle du rôle pour ce ticket.

## Rejeu

- Tag de départ : `{{baseline_tag}}`.
- Pendant un run `NNN`, les branches partent de `run/NNN` et les PR visent `run/NNN`, jamais `main`.
- Commande d'éval : {{eval_command}}

## Branches et PR

- Une branche par ticket : `<ticket>-<slug>` (préfixée `run-NNN/` pendant un run).
- Corps de PR selon le skill `mro-pr`, avec `Closes #<ticket>`.
