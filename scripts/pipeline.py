"""End-to-end scenario pipeline: fixture, render, agent run, deterministic scoring."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from agents.base import AgentAdapter
from scorers import report_shape, review_findings
from scripts.config import EvalConfig
from scripts.fixtures import build_fixture
from scripts.standards import Scenario

NO_FIXTURE_NOTE = "scenario has no deterministic fixture builder yet"


def score_scenario(
    scenario_id: str,
    report: str,
    fixture_path: Path | None,
) -> report_shape.ShapeCheck:
    """Dispatch the strongest mechanical scorer available for the scenario."""
    if scenario_id == "CR-002":
        return report_shape.check_no_padding(report)
    if scenario_id == "CR-001" and fixture_path is not None:
        return review_findings.check_cr001(report, fixture_path)
    if scenario_id == "CR-003" and fixture_path is not None:
        return review_findings.check_cr003(report, fixture_path)
    return report_shape.check(report)


@dataclass(frozen=True)
class ScenarioVerdict:
    """Outcome of one end-to-end scenario run."""

    scenario_id: str
    ok: bool
    failures: tuple[str, ...]
    report_path: Path
    fixture_path: Path | None


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
    result = adapter.run(scenario.prompt, fixture_path, scenario.scenario_id)
    (run_dir / "agent-stdout.jsonl").write_text(result.stdout, encoding="utf-8")
    (run_dir / "agent-stderr.log").write_text(result.stderr, encoding="utf-8")
    report = result.answer.strip()
    report_path = run_dir / "report.md"
    report_path.write_text(report, encoding="utf-8")
    check = score_scenario(scenario.scenario_id, report, fixture_path)
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
    }
    verdict_path = run_dir / "verdict.json"
    verdict_path.write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return verdict
