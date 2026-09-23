"""CLI: post-hoc LLM grading of saved baseline/candidate runs, key from the Kilo auth store."""

from __future__ import annotations

import argparse
import json
import os
import sys
from dataclasses import replace
from datetime import UTC, datetime
from pathlib import Path

from scorers.llm_judge import JudgeError
from scripts.config import load_config
from scripts.judge_run import grade_run_dir
from scripts.pipeline import JUDGE_SCENARIOS

DEFAULT_KILO_AUTH = Path("~/.local/share/kilo/auth.json")
DEFAULT_KILO_PROVIDER = "zai-coding-plan"


def resolve_api_key(kilo_auth: Path, provider: str) -> str:
    """Read the provider API key from the Kilo auth store."""
    data = json.loads(kilo_auth.read_text(encoding="utf-8"))
    entry = data.get(provider) if isinstance(data, dict) else None
    key = entry.get("key") if isinstance(entry, dict) else None
    if not isinstance(key, str) or not key:
        msg = f"no api key for provider {provider!r} in {kilo_auth}"
        raise JudgeError(msg)
    return key


def discover_runs(
    reports_root: Path,
    scenarios: frozenset[str],
    force: bool,
) -> list[Path]:
    """Find run dirs for judge scenarios that have no judge verdict yet."""
    found: list[Path] = []
    for verdict_path in sorted(reports_root.glob("*/verdict.json")):
        verdict = json.loads(verdict_path.read_text(encoding="utf-8"))
        if verdict.get("scenario_id") not in scenarios:
            continue
        run_dir = verdict_path.parent
        if not force and (run_dir / "judge.json").is_file():
            continue
        found.append(run_dir)
    return found


def main(argv: list[str] | None = None) -> int:
    """Grade saved CR-004/CR-006 runs; print a summary; exit 1 on judge fail."""
    parser = argparse.ArgumentParser(description="LLM-judge saved baseline runs.")
    parser.add_argument("--config", type=Path, default=Path("config.toml"))
    parser.add_argument("--reports-root", type=Path, default=Path("reports"))
    parser.add_argument("--revision", default=None, help="Only runs recorded for this revision")
    parser.add_argument("--force", action="store_true", help="Regrade judged runs")
    parser.add_argument(
        "--kilo-auth",
        type=Path,
        default=DEFAULT_KILO_AUTH,
        help="Path to the Kilo auth store holding the judge provider key",
    )
    parser.add_argument("--kilo-provider", default=DEFAULT_KILO_PROVIDER)
    args = parser.parse_args(argv)

    config = load_config(args.config, args.revision)
    if config.judge is None:
        parser.error("add the [judge] section to the config (base_url, model, api_key_env)")
    judge_config = replace(config.judge, enabled=True)
    config = replace(config, judge=judge_config)

    if not os.environ.get(judge_config.api_key_env):
        key = resolve_api_key(args.kilo_auth.expanduser(), args.kilo_provider)
        os.environ[judge_config.api_key_env] = key

    reports_root = args.reports_root.resolve()
    run_dirs = discover_runs(reports_root, JUDGE_SCENARIOS, args.force)
    if args.revision is not None:
        run_dirs = [
            run_dir
            for run_dir in run_dirs
            if json.loads((run_dir / "verdict.json").read_text(encoding="utf-8")).get(
                "standards_revision"
            )
            == args.revision
        ]
    if not run_dirs:
        print("no runs to grade")
        return 0

    results: list[dict[str, object]] = []
    for run_dir in run_dirs:
        try:
            scenario_id, record = grade_run_dir(run_dir, config)
        except JudgeError as error:
            results.append(
                {"run": run_dir.name, "scenario_id": "?", "status": "error", "error": str(error)}
            )
            print(f"{run_dir.name}: ERROR — {error}", flush=True)
            continue
        results.append(
            {
                "run": run_dir.name,
                "scenario_id": scenario_id,
                "status": record["status"],
                "score": record["score"],
                "rationale": record["rationale"],
            }
        )
        print(
            f"{run_dir.name}: {scenario_id} judge {record['status']} (score {record['score']})",
            flush=True,
        )

    stamp = datetime.now(UTC).strftime("%Y%m%d-%H%M%S")
    summary_dir = reports_root / f"{stamp}-judge-baseline"
    summary_dir.mkdir(parents=True, exist_ok=True)
    fails = [item for item in results if item["status"] == "fail"]
    errors = [item for item in results if item["status"] == "error"]
    summary = {
        "kind": "judge-baseline-summary",
        "runs": len(results),
        "pass": sum(1 for item in results if item["status"] == "pass"),
        "fail": len(fails),
        "errors": len(errors),
        "model": judge_config.model,
        "results": results,
    }
    (summary_dir / "summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(
        f"pass={summary['pass']} fail={summary['fail']} errors={summary['errors']} — {summary_dir}"
    )
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
