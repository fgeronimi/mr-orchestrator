from grid import evaluate, to_markdown

GREEN_CI = [{"__typename": "CheckRun", "name": "test", "status": "COMPLETED", "conclusion": "SUCCESS"}]


def pr(files, checks=GREEN_CI, labels=()):
    return {
        "files": [{"path": p, "additions": a, "deletions": d} for p, a, d in files],
        "statusCheckRollup": checks,
        "labels": [{"name": l} for l in labels],
    }


def statuses(result):
    return {r["criterion"]: r["status"] for r in result["rows"]}


def test_small_tested_low_risk_change_is_auto():
    result = evaluate(pr([("src/memento/api.py", 40, 5), ("tests/test_api.py", 30, 0)]),
                      ["risk:low", "repo:memento"], {})
    assert result["decision"] == "auto", statuses(result)


def test_large_diff_needs_human_but_tests_do_not_count():
    small = evaluate(pr([("src/a.py", 100, 0), ("tests/test_a.py", 500, 0)]), ["risk:low"], {})
    big = evaluate(pr([("src/a.py", 200, 0), ("tests/test_a.py", 10, 0)]), ["risk:low"], {})
    assert small["decision"] == "auto"
    assert big["decision"] == "human"


def test_sensitive_zone_from_config():
    cfg = {"sensitive_globs": ["src/memento/ingest/**"]}
    result = evaluate(pr([("src/memento/ingest/parse.py", 5, 1), ("tests/test_parse.py", 5, 0)]),
                      ["risk:low"], cfg)
    assert statuses(result)["Zones sensibles"] == "rouge"
    assert result["decision"] == "human"


def test_dependency_and_code_without_tests_and_multi_repo():
    result = evaluate(pr([("pyproject.toml", 1, 0), ("src/a.py", 3, 0)]),
                      ["risk:low", "repo:memento", "repo:kosmos"], {})
    s = statuses(result)
    assert s["Dépendances"] == s["Tests"] == s["Périmètre"] == "rouge"


def test_missing_or_high_risk_label_needs_human():
    files = [("src/a.py", 3, 0), ("tests/test_a.py", 3, 0)]
    assert evaluate(pr(files), [], {})["decision"] == "human"
    assert evaluate(pr(files), ["risk:med"], {})["decision"] == "human"


def test_eval_drop_is_red_and_missing_eval_is_neutral_unless_required():
    files = [("src/a.py", 3, 0), ("tests/test_a.py", 3, 0)]
    assert evaluate(pr(files), ["risk:low"], {}, 0.70, 0.65)["decision"] == "human"
    assert evaluate(pr(files), ["risk:low"], {})["decision"] == "auto"
    assert evaluate(pr(files), ["risk:low"], {"eval_required": True})["decision"] == "human"


def test_ci_states():
    files = [("src/a.py", 3, 0), ("tests/test_a.py", 3, 0)]
    failing = [{"name": "test", "status": "COMPLETED", "conclusion": "FAILURE"}]
    running = [{"name": "test", "status": "IN_PROGRESS", "conclusion": ""}]
    assert evaluate(pr(files, failing), ["risk:low"], {})["decision"] == "block"
    assert evaluate(pr(files, running), ["risk:low"], {})["decision"] == "wait"
    assert evaluate(pr(files, []), ["risk:low"], {})["decision"] == "human"


def test_markdown_table():
    result = evaluate(pr([("src/a.py", 3, 0), ("tests/test_a.py", 3, 0)]), ["risk:low"], {})
    md = to_markdown(result, "#12")
    assert "Auto-merge autorisé" in md and "| CI |" in md
