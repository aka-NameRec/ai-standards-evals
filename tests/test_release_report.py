"""Tests for release report aggregation."""

from __future__ import annotations

import json
from pathlib import Path

from scripts.release_report import build_release_report, collect_runs


def _write_run(root: Path, name: str, scenario: str, revision: str, ok: bool) -> None:
    run_dir = root / name
    run_dir.mkdir(parents=True, exist_ok=True)
    verdict = {
        "scenario_id": scenario,
        "standards_revision": revision,
        "ok": ok,
    }
    (run_dir / "verdict.json").write_text(
        json.dumps(verdict, ensure_ascii=False), encoding="utf-8"
    )


def _write_rescore(run_dir: Path, scenario: str, ok: bool) -> None:
    (run_dir / "rescore.json").write_text(
        json.dumps({"scenario_id": scenario, "ok": ok}, ensure_ascii=False),
        encoding="utf-8",
    )


def test_collect_runs_filters_by_revision(tmp_path: Path) -> None:
    _write_run(tmp_path, "run-a", "CR-001", "rev-a", True)
    _write_run(tmp_path, "run-b", "CR-001", "rev-b", False)

    runs = collect_runs(tmp_path, "rev-a")

    assert set(runs) == {"CR-001"}
    assert runs["CR-001"][0]["passed"] is True


def test_rescore_supersedes_original_verdict(tmp_path: Path) -> None:
    _write_run(tmp_path, "run-a", "CR-001", "rev-a", False)
    _write_rescore(tmp_path / "run-a", "CR-001", True)

    runs = collect_runs(tmp_path, "rev-a")

    assert runs["CR-001"][0]["passed"] is True


def test_release_report_fails_on_missing_scenario_runs(tmp_path: Path) -> None:
    _write_run(tmp_path, "run-a", "CR-001", "rev-a", True)

    report = build_release_report(tmp_path, "rev-a", ["CR-001", "CR-002"], 1, {})

    assert report["verdict"] == "FAIL"
    assert report["blocking"] == [
        {"scenario_id": "CR-002", "verdict": "NO RUNS", "runs": 0, "required_min_runs": 1}
    ]


def test_release_report_passes_when_all_scenarios_pass(tmp_path: Path) -> None:
    _write_run(tmp_path, "run-a", "CR-001", "rev-a", True)
    _write_run(tmp_path, "run-b", "CR-002", "rev-a", True)

    report = build_release_report(tmp_path, "rev-a", ["CR-001", "CR-002"], 1, {})

    assert report["verdict"] == "PASS"
    assert report["blocking"] == []


def test_release_report_records_waivers(tmp_path: Path) -> None:
    _write_run(tmp_path, "run-a", "CR-006", "rev-a", False)

    report = build_release_report(
        tmp_path, "rev-a", ["CR-006"], 1, {"CR-006": "known drift, tracked in #18"}
    )

    assert report["verdict"] == "PASS"
    assert report["scenarios"]["CR-006"]["waived"] == "known drift, tracked in #18"


def test_release_report_requires_min_runs(tmp_path: Path) -> None:
    _write_run(tmp_path, "run-a", "CR-001", "rev-a", True)

    report = build_release_report(tmp_path, "rev-a", ["CR-001"], 2, {})

    assert report["verdict"] == "FAIL"
    assert report["scenarios"]["CR-001"]["ok"] is False
