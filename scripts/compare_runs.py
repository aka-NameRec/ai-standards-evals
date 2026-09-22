"""CLI: compare behavioral verdicts between two standards revisions."""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import UTC, datetime
from pathlib import Path

from scripts.release_report import collect_runs

DEFAULT_SCENARIOS = ",".join(f"CR-{number:03d}" for number in range(1, 10))

_RANK = {"NO RUNS": 0, "FAIL": 1, "MIXED": 2, "PASS": 3}


def revision_verdict(runs: dict[str, list[dict[str, object]]], scenario_id: str) -> str:
    entries = runs.get(scenario_id, [])
    if not entries:
        return "NO RUNS"
    if all(bool(entry["passed"]) for entry in entries):
        return "PASS"
    if any(bool(entry["passed"]) for entry in entries):
        return "MIXED"
    return "FAIL"


def main(argv: list[str] | None = None) -> int:
    """Compare baseline and candidate verdicts; exit 1 on any candidate downgrade."""
    parser = argparse.ArgumentParser(description="Baseline vs candidate verdict comparison.")
    parser.add_argument("--baseline-revision", required=True)
    parser.add_argument("--candidate-revision", required=True)
    parser.add_argument("--reports-root", type=Path, default=Path("reports"))
    parser.add_argument("--scenarios", default=DEFAULT_SCENARIOS)
    parser.add_argument("--output", type=Path, default=None, help="Write a markdown table")
    args = parser.parse_args(argv)

    scenarios = [name.strip() for name in args.scenarios.split(",")]
    baseline_runs = collect_runs(args.reports_root, args.baseline_revision)
    candidate_runs = collect_runs(args.reports_root, args.candidate_revision)

    rows: list[dict[str, str]] = []
    downgrades: list[str] = []
    for scenario_id in scenarios:
        baseline = revision_verdict(baseline_runs, scenario_id)
        candidate = revision_verdict(candidate_runs, scenario_id)
        worse = _RANK[candidate] < _RANK[baseline]
        if worse:
            downgrades.append(f"{scenario_id}: {baseline} -> {candidate}")
        rows.append(
            {
                "scenario": scenario_id,
                "baseline": baseline,
                "candidate": candidate,
                "delta": "downgrade" if worse else ("same" if baseline == candidate else "upgrade"),
            }
        )
        state = "DOWNGRADE" if worse else delta_marker(baseline, candidate)
        print(f"{scenario_id:<8} baseline={baseline:<8} candidate={candidate:<8} {state}")

    stamp = datetime.now(UTC).strftime("%Y%m%d-%H%M%S")
    comparison = {
        "kind": "run-comparison",
        "baseline_revision": args.baseline_revision,
        "candidate_revision": args.candidate_revision,
        "generated": stamp,
        "verdict": "REJECT" if downgrades else "ACCEPT",
        "downgrades": downgrades,
        "rows": rows,
    }
    output = args.output or (
        args.reports_root
        / f"{stamp}-compare-{_safe(args.candidate_revision)}"
        / "comparison.json"
    )
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        json.dumps(comparison, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    header = f"{'scenario':<10}{'baseline':<10}{'candidate':<11}delta"
    lines = [header, "-" * len(header)]
    for row in rows:
        lines.append(
            f"{row['scenario']:<10}{row['baseline']:<10}{row['candidate']:<11}{row['delta']}"
        )
    lines.append("")
    lines.append(
        f"verdict: {comparison['verdict']}"
        + (f" ({'; '.join(downgrades)})" if downgrades else "")
    )
    table = "\n".join(lines)
    (output.parent / "comparison.txt").write_text(table + "\n", encoding="utf-8")
    print(table)
    return 1 if downgrades else 0


def delta_marker(baseline: str, candidate: str) -> str:
    if _RANK[candidate] > _RANK[baseline]:
        return "upgrade"
    return "same"


def _safe(revision: str) -> str:
    return re.sub(r"[^A-Za-z0-9._-]", "-", revision)


if __name__ == "__main__":
    sys.exit(main())
