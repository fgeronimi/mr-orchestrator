# /// script
# requires-python = ">=3.12"
# dependencies = ["pyyaml>=6"]
# ///
"""Gestion des forks de skills : création et mise à jour par fusion à 3 versions.

Chaque fork vit dans <skills_dir>/<nom>/ avec un UPSTREAM.yaml :

    repo: mattpocock/skills          # owner/repo GitHub, ou URL/chemin git
    path: skills/engineering/tdd     # dossier du skill dans l'upstream
    ref: main                        # branche suivie
    commit: <sha>                    # version upstream sur laquelle le fork est aligné
    pending: <sha>                   # (optionnel) mise à jour commencée, conflits à résoudre

Commandes :
    uv run sync_forks.py fork <repo> <path> <nom> [--ref main]
    uv run sync_forks.py check            # liste les forks en retard sur l'upstream
    uv run sync_forks.py update [<nom>]   # fusionne ; conflits marqués dans les fichiers
    uv run sync_forks.py done <nom>       # après résolution des conflits : avance le commit

Options communes : --skills-dir (défaut : skills), --cache-dir (défaut : ~/.cache/mr-orchestrator/upstream).
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from dataclasses import dataclass, field
from pathlib import Path

import yaml

UPSTREAM_FILE = "UPSTREAM.yaml"
CONFLICT_RE = re.compile(r"^<<<<<<< ", re.MULTILINE)


# --- git ---------------------------------------------------------------------

def git(*args: str, cwd: Path | None = None) -> str:
    result = subprocess.run(
        ["git", *args], cwd=cwd, check=True, capture_output=True, text=True
    )
    return result.stdout


def repo_url(repo: str) -> str:
    """owner/repo -> URL GitHub ; une URL ou un chemin local reste tel quel."""
    if re.fullmatch(r"[\w.-]+/[\w.-]+", repo) and not Path(repo).exists():
        return f"https://github.com/{repo}.git"
    return repo


def cache_path(cache_dir: Path, repo: str) -> Path:
    slug = re.sub(r"[^\w.-]+", "__", repo.strip("/"))
    return cache_dir / slug


def ensure_clone(cache_dir: Path, repo: str) -> Path:
    """Clone partiel (sans blobs) en cache, puis fetch de toutes les branches."""
    target = cache_path(cache_dir, repo)
    if not (target / ".git").exists() and not (target / "HEAD").exists():
        target.parent.mkdir(parents=True, exist_ok=True)
        git("clone", "--quiet", "--bare", "--filter=blob:none", repo_url(repo), str(target))
    git("fetch", "--quiet", "--prune", "origin", "+refs/heads/*:refs/heads/*", cwd=target)
    return target


def head_commit(clone: Path, ref: str) -> str:
    return git("rev-parse", ref, cwd=clone).strip()


def list_files(clone: Path, commit: str, path: str) -> dict[str, bytes]:
    """Fichiers du dossier `path` à `commit`, chemins relatifs à `path`."""
    prefix = path.strip("/") + "/"
    try:
        names = git("ls-tree", "-r", "--name-only", commit, "--", prefix, cwd=clone).splitlines()
    except subprocess.CalledProcessError:
        return {}
    files = {}
    for name in names:
        blob = subprocess.run(
            ["git", "show", f"{commit}:{name}"], cwd=clone, check=True, capture_output=True
        ).stdout
        files[name[len(prefix):]] = blob
    return files


# --- UPSTREAM.yaml -----------------------------------------------------------

def read_upstream(skill_dir: Path) -> dict:
    return yaml.safe_load((skill_dir / UPSTREAM_FILE).read_text()) or {}


def write_upstream(skill_dir: Path, data: dict) -> None:
    ordered = {k: data[k] for k in ("repo", "path", "ref", "commit", "pending") if data.get(k)}
    (skill_dir / UPSTREAM_FILE).write_text(yaml.safe_dump(ordered, sort_keys=False))


def find_forks(skills_dir: Path, name: str | None = None) -> list[Path]:
    forks = sorted(p.parent for p in skills_dir.glob(f"*/{UPSTREAM_FILE}"))
    if name:
        forks = [p for p in forks if p.name == name]
        if not forks:
            raise SystemExit(f"Aucun fork nommé {name!r} dans {skills_dir}")
    return forks


def local_files(skill_dir: Path) -> dict[str, bytes]:
    return {
        str(p.relative_to(skill_dir)): p.read_bytes()
        for p in skill_dir.rglob("*")
        if p.is_file() and p.name != UPSTREAM_FILE
    }


# --- fusion -------------------------------------------------------------------

@dataclass
class FileResult:
    path: str
    action: str  # unchanged | updated | added | deleted | merged | conflict | kept-local


@dataclass
class ForkReport:
    name: str
    base: str
    latest: str
    files: list[FileResult] = field(default_factory=list)

    @property
    def up_to_date(self) -> bool:
        return self.base == self.latest

    @property
    def conflicts(self) -> list[str]:
        return [f.path for f in self.files if f.action == "conflict"]

    def as_dict(self) -> dict:
        return {
            "name": self.name,
            "base": self.base,
            "latest": self.latest,
            "up_to_date": self.up_to_date,
            "conflicts": self.conflicts,
            "files": [{"path": f.path, "action": f.action} for f in self.files if f.action != "unchanged"],
        }


def merge3(ours: bytes, base: bytes, theirs: bytes, label: str) -> tuple[bytes, bool]:
    """git merge-file ; renvoie (contenu, a_des_conflits)."""
    with tempfile.TemporaryDirectory() as tmp:
        paths = []
        for name, content in (("ours", ours), ("base", base), ("theirs", theirs)):
            p = Path(tmp) / name
            p.write_bytes(content)
            paths.append(str(p))
        result = subprocess.run(
            ["git", "merge-file", "-p",
             "-L", f"fork ({label})", "-L", "base", "-L", "upstream",
             *paths],
            capture_output=True,
        )
        if result.returncode < 0 or result.returncode > 127:
            raise RuntimeError(f"git merge-file a échoué sur {label}")
        return result.stdout, result.returncode > 0


def plan_update(skill_dir: Path, base_files: dict, latest_files: dict, base: str, latest: str) -> tuple[ForkReport, dict[str, bytes | None]]:
    """Calcule le résultat de la fusion sans rien écrire. None = fichier à supprimer."""
    ours_files = local_files(skill_dir)
    report = ForkReport(skill_dir.name, base, latest)
    writes: dict[str, bytes | None] = {}

    for path in sorted(set(base_files) | set(latest_files) | set(ours_files)):
        b, t, o = base_files.get(path), latest_files.get(path), ours_files.get(path)

        if b == t:  # upstream n'a pas touché ce fichier
            report.files.append(FileResult(path, "unchanged"))
            continue
        if o == b:  # on n'a pas touché ce fichier : on prend l'upstream tel quel
            writes[path] = t
            action = "deleted" if t is None else ("added" if b is None else "updated")
            report.files.append(FileResult(path, action))
            continue
        if o == t:  # même changement des deux côtés
            report.files.append(FileResult(path, "unchanged"))
            continue
        if t is None:  # supprimé en amont, modifié chez nous : on garde, on signale
            report.files.append(FileResult(path, "kept-local"))
            continue
        merged, conflict = merge3(o or b"", b or b"", t, path)
        writes[path] = merged
        report.files.append(FileResult(path, "conflict" if conflict else "merged"))

    return report, writes


def apply_writes(skill_dir: Path, writes: dict[str, bytes | None]) -> None:
    for path, content in writes.items():
        target = skill_dir / path
        if content is None:
            if target.exists():
                target.unlink()
            continue
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(content)


# --- commandes ----------------------------------------------------------------

def cmd_fork(args) -> dict:
    skill_dir = args.skills_dir / args.name
    if skill_dir.exists():
        raise SystemExit(f"{skill_dir} existe déjà.")
    clone = ensure_clone(args.cache_dir, args.repo)
    commit = head_commit(clone, args.ref)
    files = list_files(clone, commit, args.path)
    if not files:
        raise SystemExit(f"Rien trouvé à {args.path!r} dans {args.repo}@{args.ref}.")
    apply_writes(skill_dir, files)
    write_upstream(skill_dir, {"repo": args.repo, "path": args.path.strip("/"), "ref": args.ref, "commit": commit})
    return {"forked": args.name, "commit": commit, "files": sorted(files)}


def _reports(args, apply: bool) -> list[dict]:
    out = []
    for skill_dir in find_forks(args.skills_dir, getattr(args, "name", None)):
        up = read_upstream(skill_dir)
        clone = ensure_clone(args.cache_dir, up["repo"])
        latest = head_commit(clone, up.get("ref", "main"))
        base = up["commit"]
        if base == latest:
            out.append(ForkReport(skill_dir.name, base, latest).as_dict())
            continue
        report, writes = plan_update(
            skill_dir,
            list_files(clone, base, up["path"]),
            list_files(clone, latest, up["path"]),
            base,
            latest,
        )
        if apply:
            apply_writes(skill_dir, writes)
            if report.conflicts:
                up["pending"] = latest
            else:
                up["commit"] = latest
                up.pop("pending", None)
            write_upstream(skill_dir, up)
        out.append(report.as_dict())
    return out


def cmd_check(args) -> list[dict]:
    return _reports(args, apply=False)


def cmd_update(args) -> list[dict]:
    return _reports(args, apply=True)


def cmd_done(args) -> dict:
    skill_dir = find_forks(args.skills_dir, args.name)[0]
    up = read_upstream(skill_dir)
    if not up.get("pending"):
        raise SystemExit(f"{args.name} n'a pas de mise à jour en attente.")
    remaining = [
        path for path, content in local_files(skill_dir).items()
        if CONFLICT_RE.search(content.decode("utf-8", errors="replace"))
    ]
    if remaining:
        raise SystemExit("Conflits encore présents dans : " + ", ".join(sorted(remaining)))
    up["commit"] = up.pop("pending")
    write_upstream(skill_dir, up)
    return {"done": args.name, "commit": up["commit"]}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--skills-dir", type=Path, default=Path("skills"))
    parser.add_argument(
        "--cache-dir",
        type=Path,
        default=Path(os.environ.get("XDG_CACHE_HOME", Path.home() / ".cache")) / "mr-orchestrator" / "upstream",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("fork", help="créer un fork d'un skill upstream")
    p.add_argument("repo")
    p.add_argument("path")
    p.add_argument("name")
    p.add_argument("--ref", default="main")
    p.set_defaults(func=cmd_fork)

    p = sub.add_parser("check", help="lister les forks en retard")
    p.add_argument("name", nargs="?")
    p.set_defaults(func=cmd_check)

    p = sub.add_parser("update", help="fusionner l'upstream dans les forks")
    p.add_argument("name", nargs="?")
    p.set_defaults(func=cmd_update)

    p = sub.add_parser("done", help="valider une mise à jour après résolution des conflits")
    p.add_argument("name")
    p.set_defaults(func=cmd_done)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if not shutil.which("git"):
        print("git est requis.", file=sys.stderr)
        return 1
    result = args.func(args)
    print(json.dumps(result, indent=2, ensure_ascii=False))
    if isinstance(result, list) and any(r["conflicts"] for r in result):
        return 3
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
