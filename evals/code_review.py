"""Inspect AI task wiring for the code-review behavioral suite (v0.1 slice)."""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

from inspect_ai import Task, task
from inspect_ai.dataset import Sample
from inspect_ai.scorer import CORRECT, INCORRECT, Score, Scorer, Target, accuracy, scorer
from inspect_ai.solver import Generate, Solver, TaskState, solver

from agents.kilo import KiloAdapter
from scripts.config import EvalConfig, load_config
from scripts.pipeline import run_scenario, score_scenario
from scripts.standards import index_scenarios, resolve_standards_checkout

DEFAULT_SCENARIO = "CR-002"


@task
def code_review(scenario_id: str = DEFAULT_SCENARIO, config_path: str = "config.toml") -> Task:
    """Run one behavioral scenario through the Kilo adapter and score the report shape."""
    config = load_config(Path(config_path))
    return Task(
        dataset=[
            Sample(
                input=f"Execute behavioral scenario {scenario_id} against the pinned standards.",
                metadata={"scenario_id": scenario_id},
            )
        ],
        solver=_review_solver(config, scenario_id),
        scorer=_report_scorer(scenario_id),
    )


@solver
def _review_solver(config: EvalConfig, scenario_id: str) -> Solver:
    async def solve(state: TaskState, generate: Generate) -> TaskState:
        adapter = KiloAdapter(model=config.model, timeout_seconds=config.timeout_seconds)
        with resolve_standards_checkout(config) as worktree:
            scenario = index_scenarios(worktree)[scenario_id]
            stamp = datetime.now(UTC).strftime("%Y%m%d-%H%M%S")
            run_dir = Path("reports") / f"{stamp}-{scenario_id}"
            verdict = run_scenario(config, worktree, adapter, scenario, run_dir)
        state.output.completion = verdict.report_path.read_text(encoding="utf-8")
        state.metadata["verdict"] = {"ok": verdict.ok, "failures": list(verdict.failures)}
        state.metadata["fixture_path"] = (
            str(verdict.fixture_path) if verdict.fixture_path else None
        )
        return state

    return solve


@scorer(metrics=[accuracy()])
def _report_scorer(scenario_id: str) -> Scorer:
    async def score(state: TaskState, target: Target) -> Score:
        fixture_raw = state.metadata.get("fixture_path")
        fixture_path = Path(fixture_raw) if fixture_raw else None
        check = score_scenario(scenario_id, state.output.completion, fixture_path)
        return Score(
            value=CORRECT if check.ok else INCORRECT,
            answer="shape satisfied" if check.ok else "; ".join(check.failures),
            explanation=(
                "; ".join(check.failures)
                if check.failures
                else "report shape satisfies the scenario invariants"
            ),
        )

    return score
