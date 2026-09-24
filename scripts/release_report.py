"""CLI: aggregate run artifacts into a machine-readable release verification report."""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import cast

DEFAULT_SCENARIOS = ",".join(f"CR-{number:03d}" for number in range(1, 10))


def collect_runs(reports_root: Path, revision: str) -> dict[str, list[dict[str, object]]]:
    """Group rescore-aware verdicts by scenario for the requested revision.

    Both layouts count: single-scenario run dirs (``reports/<run>/verdict.json``)
    and matrix cells (``reports/<matrix>/<adapter>/<scenario>/verdict.json``).
    Archived runs (any ``archive*`` directory) are excluded.
    """
    runs: dict[str, list[dict[str, object]]] = {}
    for verdict_path in sorted(reports_root.rglob("verdict.json")):
        if any(part.startswith("archive") for part in verdict_path.parts):
            continue
        verdict = json.loads(verdict_path.read_text(encoding="utf-8"))
        if verdict.get("standards_revision") != revision:
            continue
        scenario_id = str(verdict.get("scenario_id", ""))
        if not scenario_id:
            continue
        run_dir = verdict_path.parent
        passed = bool(verdict.get("ok"))
        failures: list[str] = list(cast("list[str]", verdict.get("failures", [])))
        rescore_path = run_dir / "rescore.json"
        if rescore_path.is_file():
            rescore = json.loads(rescore_path.read_text(encoding="utf-8"))
            if rescore.get("scenario_id") == scenario_id:
                passed = bool(rescore.get("ok"))
                failures = list(cast("list[str]", rescore.get("failures", [])))
        runs.setdefault(scenario_id, []).append(
            {"run": run_dir.name, "passed": passed, "failures": failures}
        )
    return runs


def scenario_verdict(entries: list[dict[str, object]]) -> str:
    if all(bool(entry["passed"]) for entry in entries):
        return "PASS"
    if any(bool(entry["passed"]) for entry in entries):
        return "MIXED"
    return "FAIL"


def build_release_report(
    reports_root: Path,
    revision: str,
    scenarios: list[str],
    min_runs: int,
    waivers: dict[str, str],
) -> dict[str, object]:
    """Aggregate per-scenario verdicts into the release report structure."""
    runs = collect_runs(reports_root, revision)
    scenario_reports: dict[str, object] = {}
    blocking: list[dict[str, object]] = []
    for scenario_id in scenarios:
        entries = runs.get(scenario_id, [])
        verdict = scenario_verdict(entries) if entries else "NO RUNS"
        waived = scenario_id in waivers
        sufficient = len(entries) >= min_runs and verdict == "PASS"
        ok = sufficient or waived
        if not ok:
            blocking.append(
                {
                    "scenario_id": scenario_id,
                    "verdict": verdict,
                    "runs": len(entries),
                    "required_min_runs": min_runs,
                }
            )
        scenario_reports[scenario_id] = {
            "verdict": verdict,
            "runs": len(entries),
            "passed": sum(1 for entry in entries if bool(entry["passed"])),
            "waived": waivers.get(scenario_id),
            "ok": ok,
        }
    return {
        "kind": "release-report",
        "verdict": "PASS" if not blocking else "FAIL",
        "standards_revision": revision,
        "min_runs": min_runs,
        "blocking": blocking,
        "waivers": dict(waivers),
        "scenarios": scenario_reports,
    }


def main(argv: list[str] | None = None) -> int:
    """Build the release report; exit 1 when the release does not pass."""
    parser = argparse.ArgumentParser(description="Build a release verification report.")
    parser.add_argument("--revision", required=True, help="Revision the runs were executed against")
    parser.add_argument("--reports-root", type=Path, default=Path("reports"))
    parser.add_argument("--scenarios", default=DEFAULT_SCENARIOS)
    parser.add_argument("--min-runs", type=int, default=1)
    parser.add_argument(
        "--waive",
        action="append",
        default=[],
        metavar="SCENARIO=REASON",
        help="Accept a failing scenario with a documented reason",
    )
    parser.add_argument("--output", type=Path, default=None)
    args = parser.parse_args(argv)

    waivers: dict[str, str] = {}
    for item in args.waive:
        scenario, separator, reason = item.partition("=")
        if not separator or not reason.strip():
            parser.error(f"--waive requires SCENARIO=REASON, got {item!r}")
        waivers[scenario.strip()] = reason.strip()

    scenarios = [name.strip() for name in args.scenarios.split(",")]
    report = build_release_report(
        args.reports_root, args.revision, scenarios, args.min_runs, waivers
    )
    stamp = datetime.now(UTC).strftime("%Y%m%d-%H%M%S")
    output = args.output or (
        args.reports_root
        / f"{stamp}-release-{_safe(args.revision)}"
        / "release-report.json"
    )
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(f"release verdict: {report['verdict']} — {output}")
    blocking = cast("list[dict[str, object]]", report["blocking"])
    for item in blocking:
        print(
            f"  blocking: {item['scenario_id']} verdict={item['verdict']} "
            f"runs={item['runs']}"
        )
    return 0 if report["verdict"] == "PASS" else 1


def _safe(revision: str) -> str:
    return re.sub(r"[^A-Za-z0-9._-]", "-", revision)


if __name__ == "__main__":
    sys.exit(main())
