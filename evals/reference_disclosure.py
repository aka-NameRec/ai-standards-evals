"""Inspect AI task wiring for the reference disclosure behavioral suite."""

from __future__ import annotations

import sys
from datetime import UTC, datetime
from pathlib import Path

_BOOTSTRAP = Path(__file__).resolve().parents[1]
if str(_BOOTSTRAP) not in sys.path:
    sys.path.insert(0, str(_BOOTSTRAP))

from inspect_ai import Task, task  # noqa: E402
from inspect_ai.dataset import Sample  # noqa: E402
from inspect_ai.solver import Generate, Solver, TaskState, solver  # noqa: E402

from agents.kilo import KiloAdapter  # noqa: E402
from evals.code_review import _config, _verdict_scorer  # noqa: E402
from scripts.config import EvalConfig  # noqa: E402
from scripts.pipeline import run_scenario  # noqa: E402
from scripts.standards import (  # noqa: E402
    KIND_BEHAVIOR,
    index_scenarios,
    resolve_standards_checkout,
)

RD_SCENARIO_IDS = (
    "RD-101",
    "RD-102",
    "RD-103",
    "RD-104",
    "RD-105",
    "RD-106",
    "RD-107",
    "RD-108",
    "RD-110",
    "RD-111",
)

# RD-120 is the data-driven stack matrix; it runs through
# `python -m scripts.run_reference_matrix`, which materializes one fixture per
# registry stack entry instead of one fixture per scenario id.


@task
def reference_disclosure(
    scenario_id: str = "RD-101",
    config_path: str = "config.toml",
    revision: str | None = None,
) -> Task:
    """Run one reference disclosure scenario through the Kilo adapter."""
    config = _config(config_path, revision)
    return Task(
        dataset=[
            Sample(
                input=f"Execute behavioral scenario {scenario_id} against the pinned standards.",
                id=scenario_id,
                metadata={"scenario_id": scenario_id},
            )
        ],
        solver=_reference_solver(config),
        scorer=_verdict_scorer(),
    )


@task
def reference_disclosure_suite(
    config_path: str = "config.toml", revision: str | None = None
) -> Task:
    """Run every RD behavior scenario of the revision; pass --epochs for trials."""
    config = _config(config_path, revision)
    with resolve_standards_checkout(config) as worktree:
        scenarios = sorted(
            (
                scenario
                for scenario in index_scenarios(worktree).values()
                if scenario.kind == KIND_BEHAVIOR and scenario.scenario_id.startswith("RD-")
                and scenario.scenario_id in RD_SCENARIO_IDS
            ),
            key=lambda scenario: scenario.scenario_id,
        )
    if not scenarios:
        msg = "no RD behavior scenarios found in the revision"
        raise ValueError(msg)
    dataset = [
        Sample(
            input=f"Execute behavioral scenario {scenario.scenario_id}.",
            id=scenario.scenario_id,
            metadata={"scenario_id": scenario.scenario_id},
        )
        for scenario in scenarios
    ]
    return Task(dataset=dataset, solver=_reference_solver(config), scorer=_verdict_scorer())


@solver
def _reference_solver(config: EvalConfig) -> Solver:
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
