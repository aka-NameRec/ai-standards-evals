"""Inspect AI task wiring for the cherry-pick-assessment behavioral suite."""

from __future__ import annotations

import sys
from pathlib import Path

_BOOTSTRAP = Path(__file__).resolve().parents[1]
if str(_BOOTSTRAP) not in sys.path:
    sys.path.insert(0, str(_BOOTSTRAP))

from inspect_ai import Task, task  # noqa: E402
from inspect_ai.dataset import Sample  # noqa: E402

from evals.code_review import _config, _review_solver, _verdict_scorer  # noqa: E402
from scripts.standards import (  # noqa: E402
    KIND_BEHAVIOR,
    index_scenarios,
    resolve_standards_checkout,
)

# CP-008 is the two-turn invalidation scenario; it runs through
# `python -m scripts.run_cp008`, which drives both turns against one fixture
# and re-anchors the branch heads between them.
CP_SCENARIO_IDS = (
    "CP-001",
    "CP-002",
    "CP-003",
    "CP-004",
    "CP-005",
    "CP-006",
    "CP-007",
    "CP-009",
    "CP-010",
)


@task
def cherry_pick(
    scenario_id: str = "CP-001",
    config_path: str = "config.toml",
    revision: str | None = None,
) -> Task:
    """Run one cherry-pick-assessment scenario through the Kilo adapter."""
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
def cherry_pick_suite(
    config_path: str = "config.toml", revision: str | None = None
) -> Task:
    """Run every CP behavior scenario of the revision; pass --epochs for trials."""
    config = _config(config_path, revision)
    with resolve_standards_checkout(config) as worktree:
        scenarios = sorted(
            (
                scenario
                for scenario in index_scenarios(worktree).values()
                if scenario.kind == KIND_BEHAVIOR
                and scenario.scenario_id in CP_SCENARIO_IDS
            ),
            key=lambda scenario: scenario.scenario_id,
        )
    found = {scenario.scenario_id for scenario in scenarios}
    missing = sorted(set(CP_SCENARIO_IDS) - found)
    if missing:
        msg = f"CP behavior scenarios missing from the revision: {', '.join(missing)}"
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
