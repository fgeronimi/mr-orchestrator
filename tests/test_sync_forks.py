import subprocess
from pathlib import Path

import pytest
import yaml

import sync_forks


def git(cwd, *args):
    subprocess.run(["git", *args], cwd=cwd, check=True, capture_output=True)


@pytest.fixture
def upstream(tmp_path):
    """Faux repo upstream avec un skill dans skills/engineering/tdd."""
    repo = tmp_path / "upstream"
    skill = repo / "skills" / "engineering" / "tdd"
    skill.mkdir(parents=True)
    git(repo, "init", "-q", "-b", "main")
    git(repo, "config", "user.email", "t@t")
    git(repo, "config", "user.name", "t")
    (skill / "SKILL.md").write_text("ligne 1\nligne 2\nligne 3\nligne 4\nligne 5\n")
    (skill / "notes.md").write_text("notes\n")
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", "v1")
    return repo


def commit(repo, msg="change"):
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", msg)


def run(tmp_path, *argv):
    skills = tmp_path / "skills"
    skills.mkdir(exist_ok=True)
    return sync_forks.main(["--skills-dir", str(skills), "--cache-dir", str(tmp_path / "cache"), *argv])


def upstream_yaml(tmp_path, name="tdd"):
    return yaml.safe_load((tmp_path / "skills" / name / "UPSTREAM.yaml").read_text())


def test_fork_copies_files_and_records_commit(tmp_path, upstream):
    assert run(tmp_path, "fork", str(upstream), "skills/engineering/tdd", "tdd") == 0
    fork = tmp_path / "skills" / "tdd"
    assert (fork / "SKILL.md").read_text().startswith("ligne 1")
    meta = upstream_yaml(tmp_path)
    assert meta["path"] == "skills/engineering/tdd"
    assert len(meta["commit"]) == 40


def test_clean_merge_keeps_local_change_and_takes_upstream_change(tmp_path, upstream):
    run(tmp_path, "fork", str(upstream), "skills/engineering/tdd", "tdd")
    fork = tmp_path / "skills" / "tdd"
    # notre modification en haut, celle de l'upstream en bas
    fork_skill = fork / "SKILL.md"
    fork_skill.write_text(fork_skill.read_text().replace("ligne 1", "ligne 1 (fork)"))
    up_skill = upstream / "skills/engineering/tdd/SKILL.md"
    up_skill.write_text(up_skill.read_text().replace("ligne 5", "ligne 5 (upstream)"))
    (upstream / "skills/engineering/tdd/nouveau.md").write_text("nouveau\n")
    commit(upstream)
    base = upstream_yaml(tmp_path)["commit"]

    assert run(tmp_path, "update") == 0
    text = fork_skill.read_text()
    assert "ligne 1 (fork)" in text and "ligne 5 (upstream)" in text
    assert (fork / "nouveau.md").read_text() == "nouveau\n"
    meta = upstream_yaml(tmp_path)
    assert meta["commit"] != base and "pending" not in meta


def test_conflict_is_marked_and_commit_waits_for_done(tmp_path, upstream):
    run(tmp_path, "fork", str(upstream), "skills/engineering/tdd", "tdd")
    fork_skill = tmp_path / "skills/tdd/SKILL.md"
    fork_skill.write_text(fork_skill.read_text().replace("ligne 3", "ligne 3 (fork)"))
    up_skill = upstream / "skills/engineering/tdd/SKILL.md"
    up_skill.write_text(up_skill.read_text().replace("ligne 3", "ligne 3 (upstream)"))
    commit(upstream)
    base = upstream_yaml(tmp_path)["commit"]

    assert run(tmp_path, "update") == 3
    assert "<<<<<<< fork" in fork_skill.read_text()
    meta = upstream_yaml(tmp_path)
    assert meta["commit"] == base and meta["pending"]

    with pytest.raises(SystemExit):
        run(tmp_path, "done", "tdd")
    fork_skill.write_text("ligne 1\nligne 2\nligne 3 (résolu)\nligne 4\nligne 5\n")
    assert run(tmp_path, "done", "tdd") == 0
    meta = upstream_yaml(tmp_path)
    assert meta["commit"] != base and "pending" not in meta


def test_upstream_deletion_of_untouched_file_is_applied(tmp_path, upstream):
    run(tmp_path, "fork", str(upstream), "skills/engineering/tdd", "tdd")
    (upstream / "skills/engineering/tdd/notes.md").unlink()
    commit(upstream)
    run(tmp_path, "update")
    assert not (tmp_path / "skills/tdd/notes.md").exists()


def test_check_does_not_write(tmp_path, upstream):
    run(tmp_path, "fork", str(upstream), "skills/engineering/tdd", "tdd")
    up_skill = upstream / "skills/engineering/tdd/SKILL.md"
    up_skill.write_text("tout nouveau\n")
    commit(upstream)
    before = upstream_yaml(tmp_path)
    assert run(tmp_path, "check") == 0
    assert upstream_yaml(tmp_path) == before
    assert (tmp_path / "skills/tdd/SKILL.md").read_text().startswith("ligne 1")
