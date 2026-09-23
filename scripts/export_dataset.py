"""CLI: export a dataset snapshot from the pinned standards revision.

The JSONL snapshot is documentation of record for what the suite covers; the
Inspect tasks build their datasets dynamically from the same revision, so
regenerate this file with the same command when the revision advances.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from scripts.config import load_config
from scripts.fixtures import BUILDERS
from scripts.standards import index_scenarios, resolve_standards_checkout


def dataset_records(
    scenarios: dict[str, dict[str, object]],
    builders: set[str],
) -> list[dict[str, object]]:
    """Build dataset records from a parsed scenario index (pure aggregation)."""
    records: list[dict[str, object]] = []
    for scenario_id in sorted(scenarios):
        scenario = scenarios[scenario_id]
        records.append(
            {
                "scenario_id": scenario_id,
                "title": scenario["title"],
                "kind": scenario["kind"],
                "enabled_features": scenario["enabled_features"],
                "prompt": scenario["prompt"],
                "fixture_builder": scenario_id in builders,
            }
        )
    return records


def main(argv: list[str] | None = None) -> int:
    """Export the dataset snapshot; exit 0 on success."""
    parser = argparse.ArgumentParser(description="Export the dataset snapshot.")
    parser.add_argument("--config", type=Path, default=Path("config.toml"))
    parser.add_argument("--revision", default=None, help="Override the pinned revision")
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("datasets") / "code_review.jsonl",
    )
    args = parser.parse_args(argv)

    config = load_config(args.config, args.revision)
    with resolve_standards_checkout(config) as worktree:
        index = index_scenarios(worktree)
    scenarios: dict[str, dict[str, object]] = {
        scenario_id: {
            "title": scenario.title,
            "kind": scenario.kind,
            "enabled_features": list(scenario.enabled_features),
            "prompt": scenario.prompt,
        }
        for scenario_id, scenario in index.items()
    }
    records = dataset_records(scenarios, set(BUILDERS))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", encoding="utf-8") as handle:
        for record in records:
            handle.write(json.dumps(record, ensure_ascii=False) + "\n")
    print(f"{len(records)} records — {args.output}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
