"""CLI: run scenarios across every available agent adapter and report the matrix."""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import replace
from datetime import UTC, datetime
from pathlib import Path

from agents.registry import build_adapters
from scripts.config import load_config
from scripts.pipeline import run_scenario
from scripts.standards import KIND_BEHAVIOR, index_scenarios, resolve_standards_checkout

DEFAULT_SCENARIOS = ",".join(f"CR-{number:03d}" for number in range(1, 10))


def main(argv: list[str] | None = None) -> int:
    """Run the scenario × adapter matrix; exit 1 when any cell fails."""
    parser = argparse.ArgumentParser(description="Cross-agent compatibility matrix.")
    parser.add_argument("--config", type=Path, default=Path("config.toml"))
    parser.add_argument("--reports-dir", type=Path, default=Path("reports"))
    parser.add_argument("--revision", default=None, help="Override the pinned revision")
    parser.add_argument(
        "--adapters",
        default="auto",
        help="Comma-separated adapter names or 'auto' (every installed one)",
    )
    parser.add_argument("--scenarios", default=DEFAULT_SCENARIOS)
    args = parser.parse_args(argv)

    config = load_config(args.config)
    if args.revision is not None:
        config = replace(config, standards_revision=args.revision)
    wanted = (
        None
        if args.adapters == "auto"
        else [name.strip() for name in args.adapters.split(",")]
    )
    adapters = build_adapters(
        model=config.model, timeout_seconds=config.timeout_seconds, wanted=wanted
    )
    scenario_ids = [name.strip() for name in args.scenarios.split(",")]

    stamp = datetime.now(UTC).strftime("%Y%m%d-%H%M%S")
    matrix_dir = args.reports_dir.resolve() / f"{stamp}-matrix"
    cells: dict[tuple[str, str], dict[str, object]] = {}
    with resolve_standards_checkout(config) as worktree:
        scenarios = index_scenarios(worktree)
        for adapter_name, adapter in sorted(adapters.items()):
            for scenario_id in scenario_ids:
                scenario = scenarios.get(scenario_id)
                if scenario is None or scenario.kind != KIND_BEHAVIOR:
                    reason = (
                        "scenario missing in revision"
                        if scenario is None
                        else "not a behavior scenario"
                    )
                    cells[(adapter_name, scenario_id)] = {"verdict": "n/a", "reason": reason}
                    continue
                run_dir = matrix_dir / adapter_name / scenario_id
                verdict = run_scenario(config, worktree, adapter, scenario, run_dir)
                cells[(adapter_name, scenario_id)] = {
                    "verdict": "PASS" if verdict.ok else "FAIL",
                    "failures": list(verdict.failures),
                }
                state = "PASS" if verdict.ok else "FAIL"
                print(f"{adapter_name}×{scenario_id}: {state}", flush=True)

    matrix = {
        "generated": stamp,
        "standards_revision": config.standards_revision,
        "model": config.model,
        "adapters": sorted(adapters),
        "scenarios": scenario_ids,
        "cells": {f"{adapter}|{scenario}": cell for (adapter, scenario), cell in cells.items()},
    }
    (matrix_dir / "matrix.json").write_text(
        json.dumps(matrix, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    header = f"{'scenario':<10}" + "".join(f"{name:>10}" for name in sorted(adapters))
    lines = [header, "-" * len(header)]
    for scenario_id in scenario_ids:
        row = f"{scenario_id:<10}"
        for name in sorted(adapters):
            row += f"{str(cells.get((name, scenario_id), {}).get('verdict', 'n/a')):>10}"
        lines.append(row)
    table = "\n".join(lines)
    (matrix_dir / "matrix.txt").write_text(table + "\n", encoding="utf-8")
    print(table)
    failed = [cell for cell in cells.values() if cell.get("verdict") == "FAIL"]
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
