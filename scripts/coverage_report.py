"""CLI: report rule-to-scenario coverage from the pinned standards revision."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import cast

from scripts.config import load_config
from scripts.standards import RuleRecord, index_scenarios, load_rule_map, resolve_standards_checkout


def build_coverage(
    rules: dict[str, RuleRecord],
    scenario_ids: list[str],
    scenario_kinds: dict[str, str],
) -> dict[str, object]:
    """Aggregate rule-to-scenario coverage; pure aggregation over loaded data."""
    covered: dict[str, list[str]] = {}
    uncovered: list[str] = []
    for rule_id, record in rules.items():
        if record.scenarios:
            covered[rule_id] = list(record.scenarios)
        else:
            uncovered.append(rule_id)
    return {
        "rules_total": len(rules),
        "rules_with_scenarios": len(covered),
        "rules_without_scenarios": uncovered,
        "scenarios_total": len(scenario_ids),
        "scenarios_by_kind": {
            kind: sum(1 for s in scenario_ids if scenario_kinds.get(s) == kind)
            for kind in sorted(set(scenario_kinds.values()))
        },
        "coverage": covered,
    }


def main(argv: list[str] | None = None) -> int:
    """Print the coverage table; write JSON when --output is given."""
    parser = argparse.ArgumentParser(description="Rule-to-scenario coverage report.")
    parser.add_argument("--config", type=Path, default=Path("config.toml"))
    parser.add_argument("--revision", default=None, help="Override the pinned revision")
    parser.add_argument("--output", type=Path, default=None, help="Write JSON report")
    args = parser.parse_args(argv)

    config = load_config(args.config, args.revision)
    with resolve_standards_checkout(config) as worktree:
        rules = load_rule_map(worktree)
        scenario_index = index_scenarios(worktree)
    scenario_ids = sorted(scenario_index)
    scenario_kinds = {sid: scenario.kind for sid, scenario in scenario_index.items()}

    report = build_coverage(rules, scenario_ids, scenario_kinds)
    if args.output is not None:
        args.output.write_text(
            json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )

    covered = cast("dict[str, list[str]]", report["coverage"])
    uncovered = cast("list[str]", report["rules_without_scenarios"])
    print(f"revision: {config.standards_revision}")
    print(f"rules: {report['rules_total']} ({report['rules_with_scenarios']} bound, "
          f"{len(uncovered)} without scenarios)")
    print(f"scenarios: {report['scenarios_total']} ({report['scenarios_by_kind']})")
    for rule_id in sorted(covered):
        print(f"  {rule_id}: {', '.join(covered[rule_id])}")
    for rule_id in uncovered:
        print(f"  {rule_id}: —")
    return 0


if __name__ == "__main__":
    sys.exit(main())
