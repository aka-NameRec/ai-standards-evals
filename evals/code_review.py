"""Inspect AI task wiring for the code-review behavioral suite."""

from __future__ import annotations

import sys
from dataclasses import replace
from datetime import UTC, datetime
from pathlib import Path

_BOOTSTRAP = Path(__file__).resolve().parents[1]
if str(_BOOTSTRAP) not in sys.path:
    sys.path.insert(0, str(_BOOTSTRAP))

from inspect_ai import Task, task  # noqa: E402
from inspect_ai.dataset import Sample  # noqa: E402
from inspect_ai.scorer import (  # noqa: E402
    CORRECT,
    INCORRECT,
    Score,
    Scorer,
    Target,
    accuracy,
    scorer,
)
from inspect_ai.solver import Generate, Solver, TaskState, solver  # noqa: E402

from agents.kilo import KiloAdapter  # noqa: E402
from scripts.config import EvalConfig, load_config  # noqa: E402
from scripts.pipeline import run_scenario  # noqa: E402
from scripts.standards import (  # noqa: E402
    KIND_BEHAVIOR,
    index_scenarios,
    resolve_standards_checkout,
)


@task
def code_review(
    scenario_id: str = "CR-002",
    config_path: str = "config.toml",
    revision: str | None = None,
) -> Task:
    """Run one behavioral scenario through the Kilo adapter."""
    config = _config(config_path, revision)
    return Task(
        dataset=[
            Sample(
                input=f"Execute behavioral scenario {scenario_id} against the pinned standards.",
                id=scenario_id,
                metadata={"scenario_id": scenario_id},
            )
        ],
        solver=_review_solver(config),
        scorer=_verdict_scorer(),
    )


@task
def code_review_suite(config_path: str = "config.toml", revision: str | None = None) -> Task:
    """Run every CR behavior scenario of the revision; pass --epochs for trials.

    Note: scenarios CR-004 and later exist only in revisions that carry the
    eval-scenario contracts (branch ``rules-change/18-eval-scenario-contracts``
    and descendants); the released 2.5.0 pin covers CR-001..CR-003.
    """
    config = _config(config_path, revision)
    with resolve_standards_checkout(config) as worktree:
        scenarios = sorted(
            (
                scenario
                for scenario in index_scenarios(worktree).values()
                if scenario.kind == KIND_BEHAVIOR and scenario.scenario_id.startswith("CR-")
            ),
            key=lambda scenario: scenario.scenario_id,
        )
    if not scenarios:
        msg = "no CR behavior scenarios found in the revision"
        raise ValueError(msg)
    dataset = [
        Sample(
            input=f"Execute behavioral scenario {scenario.scenario_id}.",
            id=scenario.scenario_id,
            metadata={"scenario_id": scenario.scenario_id},
        )
        for scenario in scenarios
    ]
    return Task(dataset=dataset, solver=_review_solver(config), scorer=_verdict_scorer())


def _config(config_path: str, revision: str | None) -> EvalConfig:
    path = Path(config_path)
    if not path.is_absolute():
        # inspect changes cwd to the task file's directory during loading;
        # keep configuration and artifacts anchored at the repository root.
        path = _BOOTSTRAP / path
    config = load_config(path)
    if revision is not None:
        config = replace(config, standards_revision=revision)
    return config


@solver
def _review_solver(config: EvalConfig) -> Solver:
    async def solve(state: TaskState, generate: Generate) -> TaskState:
        scenario_id = str(state.metadata["scenario_id"])
        adapter = KiloAdapter(model=config.model, timeout_seconds=config.timeout_seconds)
        with resolve_standards_checkout(config) as worktree:
            scenario = index_scenarios(worktree)[scenario_id]
            stamp = datetime.now(UTC).strftime("%Y%m%d-%H%M%S-%f")
            run_dir = _BOOTSTRAP / "reports" / f"{stamp}-{scenario_id}"
            verdict = run_scenario(config, worktree, adapter, scenario, run_dir)
        state.output.completion = verdict.report_path.read_text(encoding="utf-8")
        state.metadata["verdict"] = {"ok": verdict.ok, "failures": list(verdict.failures)}
        state.metadata["fixture_path"] = (
            str(verdict.fixture_path) if verdict.fixture_path else None
        )
        return state

    return solve


@scorer(metrics=[accuracy()])
def _verdict_scorer() -> Scorer:
    async def score(state: TaskState, target: Target) -> Score:
        verdict = state.metadata.get("verdict", {})
        ok = bool(verdict.get("ok"))
        failures = list(verdict.get("failures", []))
        return Score(
            value=CORRECT if ok else INCORRECT,
            answer="shape satisfied" if ok else "; ".join(failures),
            explanation=(
                "; ".join(failures) if failures else "report satisfies the scenario invariants"
            ),
        )

    return score
