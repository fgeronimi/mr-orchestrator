# /// script
# requires-python = ">=3.12"
# dependencies = ["pyyaml>=6"]
# ///
"""Grille de l'arbitre : décide si une PR peut être auto-mergée.

Usage :
    uv run grid.py --pr 12 [--repo owner/repo] [--issue 7 | owner/repo#7]
                   [--config docs/agents/arbiter.yaml]
                   [--eval-before 0.62 --eval-after 0.65] [--json]

Décisions :
    auto   tous les critères au vert
    human  au moins un critère rouge : revue humaine
    wait   la CI tourne encore : relancer plus tard
    block  la CI est rouge : jamais de merge

La grille est calculée ici, sans modèle. L'agent arbitre ne fait que la lire,
la publier en commentaire de PR et poser le label merge:auto ou merge:human.
"""

from __future__ import annotations

import argparse
import fnmatch
import json
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

import yaml

DEFAULT_CONFIG = {
    "max_diff_lines": 150,
    "test_globs": ["tests/**", "test/**", "**/test_*.py", "**/*_test.py", "**/*.test.*", "**/*.spec.*"],
    "code_globs": ["**/*.py", "**/*.ts", "**/*.tsx", "**/*.js", "**/*.jsx", "**/*.go", "**/*.rs"],
    "sensitive_globs": [".github/**", "docs/agents/**", ".claude/**", ".agents/**"],
    "dependency_files": [
        "pyproject.toml", "uv.lock", "requirements*.txt",
        "package.json", "package-lock.json", "pnpm-lock.yaml", "yarn.lock",
        "go.mod", "Cargo.toml",
    ],
    "auto_merge_risk_labels": ["risk:low"],
    "eval_required": False,
}

GREEN, RED, PENDING, NEUTRAL = "vert", "rouge", "en cours", "non mesuré"


def matches(path: str, globs: list[str]) -> bool:
    for g in globs:
        if fnmatch.fnmatch(path, g):
            return True
        if g.startswith("**/") and fnmatch.fnmatch(path, g[3:]):
            return True
    return False


@dataclass
class Row:
    criterion: str
    status: str
    detail: str


def ci_row(checks: list[dict]) -> Row:
    if not checks:
        return Row("CI", RED, "aucun check : la CI doit tourner et être verte")
    failed, pending = [], []
    for c in checks:
        name = c.get("name") or c.get("context") or "?"
        if c.get("__typename") == "StatusContext" or "state" in c and "conclusion" not in c:
            state = (c.get("state") or "").upper()
            if state in ("PENDING", "EXPECTED"):
                pending.append(name)
            elif state not in ("SUCCESS",):
                failed.append(name)
            continue
        if (c.get("status") or "").upper() != "COMPLETED":
            pending.append(name)
        elif (c.get("conclusion") or "").upper() not in ("SUCCESS", "NEUTRAL", "SKIPPED"):
            failed.append(name)
    if failed:
        return Row("CI", RED, "en échec : " + ", ".join(failed))
    if pending:
        return Row("CI", PENDING, "en cours : " + ", ".join(pending))
    return Row("CI", GREEN, f"{len(checks)} check(s) au vert")


def evaluate(pr: dict, issue_labels: list[str], config: dict,
             eval_before: float | None = None, eval_after: float | None = None) -> dict:
    cfg = {**DEFAULT_CONFIG, **(config or {})}
    files = pr.get("files") or []
    paths = [f["path"] for f in files]
    labels = set(issue_labels) | {l["name"] for l in pr.get("labels") or []}
    rows: list[Row] = [ci_row(pr.get("statusCheckRollup") or [])]

    non_test = [f for f in files if not matches(f["path"], cfg["test_globs"])]
    size = sum(f.get("additions", 0) + f.get("deletions", 0) for f in non_test)
    rows.append(Row(
        "Taille du diff", GREEN if size <= cfg["max_diff_lines"] else RED,
        f"{size} lignes hors tests (seuil {cfg['max_diff_lines']})",
    ))

    sensitive = [p for p in paths if matches(p, cfg["sensitive_globs"])]
    rows.append(Row(
        "Zones sensibles", RED if sensitive else GREEN,
        ", ".join(sensitive) if sensitive else "aucune touchée",
    ))

    deps = [p for p in paths if matches(Path(p).name, cfg["dependency_files"]) or matches(p, cfg["dependency_files"])]
    rows.append(Row(
        "Dépendances", RED if deps else GREEN,
        "fichiers de dépendances modifiés : " + ", ".join(deps) if deps else "aucun fichier de dépendances touché",
    ))

    if eval_before is None or eval_after is None:
        status = RED if cfg["eval_required"] else NEUTRAL
        rows.append(Row("Score d'éval", status, "pas de mesure avant/après"))
    else:
        delta = eval_after - eval_before
        rows.append(Row(
            "Score d'éval", GREEN if delta >= 0 else RED,
            f"{eval_before:.3f} → {eval_after:.3f} ({delta:+.3f})",
        ))

    code_changed = [p for p in paths if matches(p, cfg["code_globs"]) and not matches(p, cfg["test_globs"])]
    tests_changed = [p for p in paths if matches(p, cfg["test_globs"])]
    if code_changed and not tests_changed:
        rows.append(Row("Tests", RED, "code modifié sans test : " + ", ".join(code_changed)))
    else:
        rows.append(Row("Tests", GREEN, f"{len(tests_changed)} fichier(s) de test touché(s)"))

    repos = sorted(l for l in labels if l.startswith("repo:"))
    rows.append(Row(
        "Périmètre", RED if len(repos) > 1 else GREEN,
        ", ".join(repos) if repos else "aucun label repo:* (un seul repo supposé)",
    ))

    risk = sorted(l for l in labels if l.startswith("risk:"))
    ok_risk = bool(risk) and all(r in cfg["auto_merge_risk_labels"] for r in risk)
    rows.append(Row(
        "Risque du ticket", GREEN if ok_risk else RED,
        ", ".join(risk) if risk else "aucun label risk:*",
    ))

    statuses = {r.status for r in rows}
    if rows[0].status == RED and rows[0].detail.startswith("en échec"):
        decision = "block"
    elif PENDING in statuses:
        decision = "wait"
    elif RED in statuses:
        decision = "human"
    else:
        decision = "auto"
    return {"decision": decision, "rows": [r.__dict__ for r in rows]}


def to_markdown(result: dict, pr_ref: str) -> str:
    label = {
        "auto": "**Auto-merge autorisé** (`merge:auto`)",
        "human": "**Revue humaine demandée** (`merge:human`)",
        "wait": "**En attente** : la CI tourne encore",
        "block": "**Bloqué** : CI rouge, pas de merge",
    }[result["decision"]]
    lines = [
        f"### Arbitrage de {pr_ref}",
        "",
        label,
        "",
        "| Critère | État | Détail |",
        "| --- | --- | --- |",
    ]
    icon = {GREEN: "🟢", RED: "🔴", PENDING: "🟡", NEUTRAL: "⚪"}
    for r in result["rows"]:
        lines.append(f"| {r['criterion']} | {icon[r['status']]} {r['status']} | {r['detail']} |")
    return "\n".join(lines) + "\n"


# --- récupération via gh -------------------------------------------------------

def gh_json(*args: str) -> dict:
    out = subprocess.run(["gh", *args], check=True, capture_output=True, text=True).stdout
    return json.loads(out)


ISSUE_RE = re.compile(r"(?:close[sd]?|fix(?:e[sd])?|resolve[sd]?)\s+((?:[\w.-]+/[\w.-]+)?#\d+)", re.IGNORECASE)


def issue_labels(issue_ref: str | None, default_repo: str | None) -> list[str]:
    if not issue_ref:
        return []
    repo, _, number = issue_ref.rpartition("#")
    args = ["issue", "view", number or issue_ref, "--json", "labels"]
    if repo or default_repo:
        args += ["--repo", repo or default_repo]
    return [l["name"] for l in gh_json(*args).get("labels", [])]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--pr", required=True)
    parser.add_argument("--repo")
    parser.add_argument("--issue", help="numéro ou owner/repo#N ; sinon lu dans « Closes #N » de la PR")
    parser.add_argument("--config", type=Path, default=Path("docs/agents/arbiter.yaml"))
    parser.add_argument("--eval-before", type=float)
    parser.add_argument("--eval-after", type=float)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)

    config = yaml.safe_load(args.config.read_text()) if args.config.exists() else {}
    view = ["pr", "view", args.pr, "--json", "files,labels,statusCheckRollup,body,url"]
    if args.repo:
        view += ["--repo", args.repo]
    pr = gh_json(*view)

    issue_ref = args.issue
    if not issue_ref:
        m = ISSUE_RE.search(pr.get("body") or "")
        issue_ref = m.group(1) if m else None
    result = evaluate(pr, issue_labels(issue_ref, args.repo), config, args.eval_before, args.eval_after)
    result["pr"] = pr.get("url")
    result["issue"] = issue_ref

    if args.json:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print(to_markdown(result, pr.get("url") or f"#{args.pr}"))
    return {"auto": 0, "human": 10, "wait": 20, "block": 30}[result["decision"]]


if __name__ == "__main__":
    raise SystemExit(main())
