"""End-to-end scenario pipeline: fixture, render, agent run, deterministic scoring."""

from __future__ import annotations

import json
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from typing import cast

from agents.base import AgentAdapter
from scorers import report_shape, review_findings
from scorers.llm_judge import (
    RUBRICS_DIR,
    HttpxJsonClient,
    JudgeError,
    judge_report,
    load_rubric,
)
from scripts.config import EvalConfig
from scripts.fixtures import build_fixture
from scripts.oracle import changed_files, diff_patch
from scripts.standards import Scenario

JUDGE_SCENARIOS = frozenset({"CR-004", "CR-006"})
NO_FIXTURE_NOTE = "scenario has no deterministic fixture builder yet"


def _run_judge(
    config: EvalConfig,
    scenario_id: str,
    run_dir: Path,
    report: str,
    diff_text: str,
    fixture_path: Path,
) -> tuple[dict[str, object] | None, bool]:
    """Grade finding depth when the judge is enabled; errors never punish the agent."""
    judge_config = config.judge
    if judge_config is None or not judge_config.enabled or scenario_id not in JUDGE_SCENARIOS:
        return None, True
    try:
        rubric = load_rubric(RUBRICS_DIR, scenario_id)
    except JudgeError as error:
        return {"status": "error", "model": judge_config.model, "error": str(error)}, True
    context = _judge_context(scenario_id, fixture_path)
    try:
        judge_verdict = judge_report(
            rubric, report, diff_text, context, judge_config, HttpxJsonClient()
        )
    except JudgeError as error:
        return {"status": "error", "model": judge_config.model, "error": str(error)}, True
    failures = (
        []
        if judge_verdict.status == "pass"
        else [f"judge rubric not met: {judge_verdict.rationale}"]
    )
    (run_dir / "judge-response.json").write_text(
        judge_verdict.raw_response, encoding="utf-8"
    )
    return {
        "status": judge_verdict.status,
        "model": judge_verdict.model,
        "score": judge_verdict.score,
        "rationale": judge_verdict.rationale,
        "criteria": judge_verdict.criteria,
        "failures": failures,
    }, judge_verdict.status == "pass"


def _judge_context(scenario_id: str, fixture_path: Path) -> str:
    extra: dict[str, Path] = {
        "CR-006": fixture_path / "docs" / "decisions" / "ADR-004.md",
    }
    path = extra.get(scenario_id)
    if path is not None and path.is_file():
        return path.read_text(encoding="utf-8")
    return "(no additional context)"


_SCENARIO_CHECKS: dict[str, Callable[[str, set[str], Path], report_shape.ShapeCheck]] = {
    "CR-001": review_findings.check_cr001,
    "CR-003": review_findings.check_cr003,
    "CR-004": review_findings.check_cr004,
    "CR-005": review_findings.check_cr005,
    "CR-006": review_findings.check_cr006,
    "CR-007": review_findings.check_cr007,
    "CR-008": review_findings.check_cr008,
    "CR-009": review_findings.check_cr009,
}


def score_scenario(
    scenario_id: str,
    report: str,
    changed: set[str],
    fixture_path: Path | None,
) -> report_shape.ShapeCheck:
    """Dispatch the strongest mechanical scorer available for the scenario.

    ``changed`` is the reviewed diff snapshot taken before the agent runs, so
    scope judgments never depend on tree mutations the agent may make;
    ``fixture_path`` lets evidence checks read the cited lines.
    """
    if scenario_id == "CR-002":
        return report_shape.check_no_padding(report)
    check = _SCENARIO_CHECKS.get(scenario_id)
    if check is not None and fixture_path is not None:
        return check(report, changed, fixture_path)
    return report_shape.check(report)


@dataclass(frozen=True)
class ScenarioVerdict:
    """Outcome of one end-to-end scenario run."""

    scenario_id: str
    ok: bool
    failures: tuple[str, ...]
    report_path: Path
    fixture_path: Path | None
    judge: dict[str, object] | None = None


def run_scenario(
    config: EvalConfig,
    worktree: Path,
    adapter: AgentAdapter,
    scenario: Scenario,
    run_dir: Path,
) -> ScenarioVerdict:
    """Build the fixture, run the agent, score the report, and persist artifacts."""
    run_dir = run_dir.resolve()
    run_dir.mkdir(parents=True, exist_ok=True)
    fixture_path = build_fixture(
        scenario.scenario_id,
        worktree,
        run_dir / "fixture",
        config.standards_revision,
    )
    if fixture_path is None:
        report_path = run_dir / "report.md"
        report_path.write_text("", encoding="utf-8")
        return ScenarioVerdict(
            scenario_id=scenario.scenario_id,
            ok=False,
            failures=(NO_FIXTURE_NOTE,),
            report_path=report_path,
            fixture_path=None,
        )
    # Snapshot the reviewed diff BEFORE the agent runs: a compliant agent may
    # mutate the tree (small fixes revert files to their HEAD state), and the
    # scope judgment must stay anchored to the diff the agent was given.
    reviewed_diff = changed_files(fixture_path)
    diff_text = diff_patch(fixture_path)
    (run_dir / "reviewed-diff.patch").write_text(diff_text, encoding="utf-8")
    result = adapter.run(scenario.prompt, fixture_path, scenario.scenario_id)
    (run_dir / "agent-stdout.jsonl").write_text(result.stdout, encoding="utf-8")
    (run_dir / "agent-stderr.log").write_text(result.stderr, encoding="utf-8")
    report = result.answer.strip()
    report_path = run_dir / "report.md"
    report_path.write_text(report, encoding="utf-8")
    check = score_scenario(
        scenario.scenario_id, report, reviewed_diff, fixture_path
    )
    judge_block, judge_ok = _run_judge(
        config, scenario.scenario_id, run_dir, report, diff_text, fixture_path
    )
    judge_failures = (
        []
        if judge_block is None
        else list(cast("list[str]", judge_block.get("failures", [])))
    )
    verdict = ScenarioVerdict(
        scenario_id=scenario.scenario_id,
        ok=check.ok and judge_ok,
        failures=check.failures + tuple(f"judge: {f}" for f in judge_failures),
        report_path=report_path,
        fixture_path=fixture_path,
        judge=judge_block,
    )
    verdict = ScenarioVerdict(
        scenario_id=scenario.scenario_id,
        ok=check.ok,
        failures=check.failures,
        report_path=report_path,
        fixture_path=fixture_path,
    )
    summary = {
        "scenario_id": verdict.scenario_id,
        "ok": verdict.ok,
        "failures": list(verdict.failures),
        "adapter": result.adapter,
        "returncode": result.returncode,
        "duration_seconds": round(result.duration_seconds, 1),
        "model": config.model,
        "standards_revision": config.standards_revision,
        "command": list(result.command),
        "judge": verdict.judge,
    }
    verdict_path = run_dir / "verdict.json"
    verdict_path.write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return verdict
