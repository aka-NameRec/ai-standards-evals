"""Tests for baseline/candidate run comparison."""

from __future__ import annotations

import json
from pathlib import Path

from scripts.compare_runs import downgrade_reason, main, revision_verdict
from scripts.release_report import collect_runs


def _write_run(
    root: Path,
    name: str,
    scenario: str,
    revision: str,
    ok: bool,
    failures: list[str] | None = None,
) -> None:
    run_dir = root / name
    run_dir.mkdir(parents=True, exist_ok=True)
    (run_dir / "verdict.json").write_text(
        json.dumps(
            {
                "scenario_id": scenario,
                "standards_revision": revision,
                "ok": ok,
                "failures": failures or [],
            },
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


def test_compare_rejects_new_substantive_failure_class(tmp_path: Path) -> None:
    _write_run(tmp_path, "base", "CR-001", "rev-a", True)
    _write_run(
        tmp_path,
        "cand",
        "CR-001",
        "rev-b",
        False,
        ["the audit-log retention class is not flagged anywhere"],
    )

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
    assert comparison["downgrades"] == [
        "CR-001: new substantive failure class absent from the baseline"
    ]


def test_compare_ignores_formatting_variance(tmp_path: Path) -> None:
    """One formatting slip on the candidate while the baseline is clean is not a
    downgrade: the model produces it stochastically on both sides."""
    _write_run(tmp_path, "base", "CR-001", "rev-a", True)
    _write_run(
        tmp_path,
        "cand",
        "CR-001",
        "rev-b",
        False,
        ["missing ai-standards version line or 'version is undetermined'"],
    )

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


def test_compare_rejects_dishonesty_failure(tmp_path: Path) -> None:
    _write_run(tmp_path, "base", "CR-001", "rev-a", True)
    _write_run(
        tmp_path,
        "cand",
        "CR-001",
        "rev-b",
        False,
        ["manufactured finding in Correctness"],
    )

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
    assert comparison["downgrades"] == ["CR-001: dishonesty failure absent from the baseline"]


def test_compare_rejects_majority_substantive_breakdown(tmp_path: Path) -> None:
    _write_run(tmp_path, "base", "CR-001", "rev-a", True)
    _write_run(
        tmp_path,
        "base-flake",
        "CR-001",
        "rev-a",
        False,
        ["the uncovered error branch is not flagged as a Quality concern"],
    )
    _write_run(
        tmp_path,
        "cand",
        "CR-001",
        "rev-b",
        False,
        ["pre-existing defect is not reported with a (pre-existing) mark"],
    )
    _write_run(
        tmp_path,
        "cand2",
        "CR-001",
        "rev-b",
        False,
        ["the uncovered error branch is not flagged as a Quality concern"],
    )

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
    assert comparison["downgrades"] == [
        "CR-001: substantive failures in the majority of candidate epochs"
    ]


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


def test_downgrade_reason_requires_baseline_evidence_for_majority_rule() -> None:
    """The majority rule needs baseline runs: with no baseline the new-class
    rule fires instead, with the same blocking outcome."""
    same_class = "correctness defect is not flagged"
    baseline = [
        {"passed": True, "failures": []},
        {"passed": False, "failures": [same_class]},
    ]
    candidate = [
        {"passed": False, "failures": [same_class]},
        {"passed": False, "failures": [same_class]},
    ]
    assert (
        downgrade_reason(baseline, candidate)
        == "substantive failures in the majority of candidate epochs"
    )
    assert (
        downgrade_reason([], candidate)
        == "new substantive failure class absent from the baseline"
    )
