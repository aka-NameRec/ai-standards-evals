"""Tests for the judge-baseline automation (key resolution, run discovery)."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from scorers.llm_judge import JudgeError
from scripts.judge_baseline import discover_runs, resolve_api_key


def _write_auth(path: Path, provider: str, key: str | None) -> None:
    entry: dict[str, object] = {"type": "api"}
    if key is not None:
        entry["key"] = key
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({provider: entry}), encoding="utf-8")


def _write_run(root: Path, name: str, scenario: str, with_judge: bool = False) -> Path:
    run_dir = root / name
    run_dir.mkdir(parents=True, exist_ok=True)
    (run_dir / "verdict.json").write_text(
        json.dumps({"scenario_id": scenario, "standards_revision": "rev-a", "ok": True}),
        encoding="utf-8",
    )
    if with_judge:
        (run_dir / "judge.json").write_text("{}", encoding="utf-8")
    return run_dir


def test_resolve_api_key_reads_kilo_store(tmp_path: Path) -> None:
    auth = tmp_path / "auth.json"
    _write_auth(auth, "zai-coding-plan", "zk-secret")

    assert resolve_api_key(auth, "zai-coding-plan") == "zk-secret"


def test_resolve_api_key_raises_for_missing_provider(tmp_path: Path) -> None:
    auth = tmp_path / "auth.json"
    _write_auth(auth, "other-provider", "k")

    with pytest.raises(JudgeError) as excinfo:
        resolve_api_key(auth, "zai-coding-plan")

    assert "no api key" in str(excinfo.value)


def test_discover_runs_skips_graded_runs(tmp_path: Path) -> None:
    _write_run(tmp_path, "run-1", "CR-004")
    _write_run(tmp_path, "run-2", "CR-006", with_judge=True)
    _write_run(tmp_path, "run-3", "CR-002")  # not a judge scenario

    found = discover_runs(tmp_path, frozenset({"CR-004", "CR-006"}), force=False)

    assert found == [tmp_path / "run-1"]


def test_discover_runs_force_includes_graded(tmp_path: Path) -> None:
    _write_run(tmp_path, "run-1", "CR-006", with_judge=True)

    found = discover_runs(tmp_path, frozenset({"CR-006"}), force=True)

    assert found == [tmp_path / "run-1"]
