"""CLI: grade a saved run's report with the LLM judge (post-hoc)."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from scorers.llm_judge import (
    RUBRICS_DIR,
    HttpJsonClient,
    HttpxJsonClient,
    JudgeError,
    judge_report,
    load_rubric,
)
from scripts.config import EvalConfig, load_config
from scripts.standards import index_scenarios, resolve_standards_checkout


class _RealClient:
    """Default HTTP double backed by the judge module's httpx client."""

    def post_json(
        self, url: str, headers: dict[str, str], payload: dict[str, object]
    ) -> dict[str, object]:
        return HttpxJsonClient().post_json(url, headers, payload)


def grade_run_dir(
    run_dir: Path,
    config: EvalConfig,
    client: HttpJsonClient | None = None,
) -> tuple[str, dict[str, object]]:
    """Grade one saved run dir; write judge.json and update verdict.json.

    Returns the scenario id and the judge record. ``client`` injects the HTTP
    double in tests; the default is the real httpx client.
    """
    run_dir = run_dir.resolve()
    verdict_path = run_dir / "verdict.json"
    verdict = json.loads(verdict_path.read_text(encoding="utf-8"))
    scenario_id = str(verdict.get("scenario_id", ""))
    report_path = run_dir / "report.md"
    diff_path = run_dir / "reviewed-diff.patch"

    with resolve_standards_checkout(config) as worktree:
        index_scenarios(worktree)  # validates the pinned revision resolves
        rubric = load_rubric(RUBRICS_DIR, scenario_id)
    report = report_path.read_text(encoding="utf-8")
    diff = diff_path.read_text(encoding="utf-8") if diff_path.is_file() else "(diff unavailable)"
    fixture = run_dir / "fixture"
    context = (
        (fixture / "docs" / "decisions" / "ADR-004.md").read_text(encoding="utf-8")
        if scenario_id == "CR-006" and (fixture / "docs" / "decisions" / "ADR-004.md").is_file()
        else "(no additional context)"
    )

    judge_config = config.judge
    if judge_config is None:
        msg = "the [judge] section is missing in the config"
        raise JudgeError(msg)
    judged = judge_report(
        rubric,
        report,
        diff,
        context,
        judge_config,
        client if client is not None else _RealClient(),
    )

    judge_record: dict[str, object] = {
        "status": judged.status,
        "model": judged.model,
        "score": judged.score,
        "rationale": judged.rationale,
        "criteria": judged.criteria,
    }
    (run_dir / "judge.json").write_text(
        json.dumps(judge_record, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    verdict["judge"] = judge_record
    verdict_path.write_text(
        json.dumps(verdict, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    return scenario_id, judge_record


def main(argv: list[str] | None = None) -> int:
    """Grade one saved run dir; write judge.json and update verdict.json."""
    parser = argparse.ArgumentParser(description="Grade a saved run with the LLM judge.")
    parser.add_argument("--run-dir", type=Path, required=True)
    parser.add_argument("--config", type=Path, default=Path("config.toml"))
    parser.add_argument("--revision", default=None, help="Override the pinned revision")
    args = parser.parse_args(argv)

    config = load_config(args.config, args.revision)
    if config.judge is None:
        parser.error(
            "the [judge] section is missing in the config "
            "(base_url, model, api_key_env are required for grading)"
        )

    try:
        scenario_id, judge_record = grade_run_dir(args.run_dir, config)
    except JudgeError as error:
        print(f"judge error: {error}")
        return 2

    print(
        f"{scenario_id}: judge {judge_record['status']} "
        f"(score {judge_record['score']}) — {args.run_dir}"
    )
    return 0 if judge_record["status"] == "pass" else 1


if __name__ == "__main__":
    sys.exit(main())
