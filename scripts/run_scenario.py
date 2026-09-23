"""CLI: execute one behavioral scenario end-to-end."""

from __future__ import annotations

import argparse
import sys
from datetime import UTC, datetime
from pathlib import Path

from agents.kilo import KiloAdapter
from scripts.config import load_config
from scripts.pipeline import run_scenario
from scripts.standards import KIND_TRIGGER_SET, index_scenarios, resolve_standards_checkout


def main(argv: list[str] | None = None) -> int:
    """Run one scenario and print a verdict summary; exit 1 on failure."""
    parser = argparse.ArgumentParser(description="Run one behavioral scenario end-to-end.")
    parser.add_argument("scenario_id", help="Scenario ID from the standards docs, e.g. CR-002")
    parser.add_argument("--config", type=Path, default=Path("config.toml"))
    parser.add_argument("--reports-dir", type=Path, default=Path("reports"))
    parser.add_argument(
        "--revision",
        default=None,
        help="Override the pinned standards revision (tag, branch, or commit)",
    )
    args = parser.parse_args(argv)

    config = load_config(args.config, args.revision)
    adapter = KiloAdapter(model=config.model, timeout_seconds=config.timeout_seconds)
    with resolve_standards_checkout(config) as worktree:
        scenarios = index_scenarios(worktree)
        if args.scenario_id not in scenarios:
            known = ", ".join(sorted(scenarios))
            parser.error(f"unknown scenario {args.scenario_id!r}; known: {known}")
        scenario = scenarios[args.scenario_id]
        if scenario.kind == KIND_TRIGGER_SET:
            parser.error(
                f"{args.scenario_id} is an activation trigger set; "
                "run it with `python -m scripts.run_triggers` instead"
            )
        stamp = datetime.now(UTC).strftime("%Y%m%d-%H%M%S")
        run_dir = args.reports_dir / f"{stamp}-{args.scenario_id}"
        verdict = run_scenario(config, worktree, adapter, scenario, run_dir)
    print(f"{verdict.scenario_id}: {'PASS' if verdict.ok else 'FAIL'} — {verdict.report_path}")
    for failure in verdict.failures:
        print(f"  - {failure}")
    return 0 if verdict.ok else 1


if __name__ == "__main__":
    sys.exit(main())
