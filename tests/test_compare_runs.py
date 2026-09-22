"""Tests for baseline/candidate run comparison."""

from __future__ import annotations

import json
from pathlib import Path

from scripts.compare_runs import main, revision_verdict
from scripts.release_report import collect_runs


def _write_run(root: Path, name: str, scenario: str, revision: str, ok: bool) -> None:
    run_dir = root / name
    run_dir.mkdir(parents=True, exist_ok=True)
    (run_dir / "verdict.json").write_text(
        json.dumps(
            {"scenario_id": scenario, "standards_revision": revision, "ok": ok},
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )


def test_revision_verdict_ranks_runs(tmp_path: Path) -> None:
    _write_run(tmp_path, "run-a", "CR-001", "rev-a", True)
    _write_run(tmp_path, "run-b", "CR-002", "rev-a", True)
    _write_run(tmp_path, "run-c", "CR-002", "rev-a", False)

    runs = collect_runs(tmp_path, "rev-a")

    assert revision_verdict(runs, "CR-001") == "PASS"
    assert revision_verdict(runs, "CR-002") == "MIXED"
    assert revision_verdict(runs, "CR-003") == "NO RUNS"


def test_compare_rejects_downgrade(tmp_path: Path) -> None:
    _write_run(tmp_path, "base", "CR-001", "rev-a", True)
    _write_run(tmp_path, "cand", "CR-001", "rev-b", False)

    code = main(
        [
            "--baseline-revision",
            "rev-a",
            "--candidate-revision",
            "rev-b",
            "--reports-root",
            str(tmp_path),
            "--output",
            str(tmp_path / "comparison.json"),
        ]
    )

    assert code == 1
    comparison = json.loads((tmp_path / "comparison.json").read_text(encoding="utf-8"))
    assert comparison["verdict"] == "REJECT"
    assert comparison["downgrades"] == ["CR-001: PASS -> FAIL"]


def test_compare_accepts_stable_or_better(tmp_path: Path) -> None:
    _write_run(tmp_path, "base", "CR-001", "rev-a", False)
    _write_run(tmp_path, "base2", "CR-001", "rev-a", True)
    _write_run(tmp_path, "cand", "CR-001", "rev-b", True)
    _write_run(tmp_path, "base3", "CR-002", "rev-a", True)
    _write_run(tmp_path, "cand2", "CR-002", "rev-b", True)

    code = main(
        [
            "--baseline-revision",
            "rev-a",
            "--candidate-revision",
            "rev-b",
            "--reports-root",
            str(tmp_path),
            "--output",
            str(tmp_path / "comparison.json"),
        ]
    )

    assert code == 0
    comparison = json.loads((tmp_path / "comparison.json").read_text(encoding="utf-8"))
    assert comparison["verdict"] == "ACCEPT"
