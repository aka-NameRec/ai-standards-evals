"""CLI: execute an activation trigger set case by case against a skill-enabled fixture."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import UTC, datetime
from pathlib import Path

from agents.kilo import KiloAdapter, skill_invoked
from scorers import report_shape
from scripts.config import load_config
from scripts.fixtures import BUILDERS
from scripts.standards import KIND_TRIGGER_SET, index_scenarios, resolve_standards_checkout

TRG_FIXTURE_BUILDERS = ("TRG-001", "TRG-003")
# Procedure skills activate by the skill tool call; report-shaped skills by
# the standard report in the answer.
SKILL_INVOCATION_SETS = frozenset({"TRG-003"})


def main(argv: list[str] | None = None) -> int:
    """Run every case of a trigger set; exit 1 when any case fails."""
    parser = argparse.ArgumentParser(description="Run one activation trigger set.")
    parser.add_argument("trigger_set_id", nargs="?", default="TRG-001")
    parser.add_argument("--config", type=Path, default=Path("config.toml"))
    parser.add_argument("--reports-dir", type=Path, default=Path("reports"))
    parser.add_argument("--index", type=int, default=None, help="Run only the Nth case (1-based)")
    args = parser.parse_args(argv)

    config = load_config(args.config)
    adapter = KiloAdapter(model=config.model, timeout_seconds=config.timeout_seconds)
    with resolve_standards_checkout(config) as worktree:
        trigger = index_scenarios(worktree)[args.trigger_set_id]
        if trigger.kind != KIND_TRIGGER_SET:
            parser.error(f"{args.trigger_set_id} is not an activation trigger set")
        cases = list(trigger.trigger_cases)
        if args.index is not None:
            if not 1 <= args.index <= len(cases):
                parser.error(f"--index must be 1..{len(cases)}")
            cases = [cases[args.index - 1]]
        fixture_builder = BUILDERS.get(args.trigger_set_id)
        if fixture_builder is None or args.trigger_set_id not in TRG_FIXTURE_BUILDERS:
            parser.error(
                f"no fixture builder for trigger set {args.trigger_set_id!r}; "
                f"known: {', '.join(TRG_FIXTURE_BUILDERS)}"
            )
        reports_root = (args.reports_dir).resolve() / (
            f"{datetime.now(UTC).strftime('%Y%m%d-%H%M%S')}-{args.trigger_set_id}"
        )
        results = []
        for index, case in enumerate(cases, start=args.index if args.index else 1):
            run_dir = reports_root / f"case-{index:02d}"
            run_dir.mkdir(parents=True, exist_ok=True)
            fixture = fixture_builder(
                worktree, run_dir / "fixture", config.standards_revision, _render
            )
            result = adapter.run(case.prompt, fixture, f"{args.trigger_set_id}-{index:02d}")
            answer = result.answer.strip()
            (run_dir / "answer.md").write_text(answer, encoding="utf-8")
            (run_dir / "agent-stdout.jsonl").write_text(result.stdout, encoding="utf-8")
            skill_seen = skill_invoked(result.stdout)
            # Activation signal per skill: the code-review skill answers with a
            # standard report; procedure skills activate by the skill tool call.
            if args.trigger_set_id in SKILL_INVOCATION_SETS:
                engaged = skill_seen
                miss_note = "expected activation, skill tool not invoked"
            else:
                engaged = report_shape.check(answer).ok
                miss_note = "expected activation, no standard report produced"
            if case.should_trigger:
                ok = engaged
                note = "" if engaged else miss_note
            else:
                ok = (not engaged) or (not skill_seen)
                note = "skill invoked on a negative case" if engaged and skill_seen else ""
            verdict = {
                "index": index,
                "prompt": case.prompt,
                "expected_should_trigger": case.should_trigger,
                "engaged": engaged,
                "skill_seen": skill_seen,
                "ok": ok,
                "note": note,
                "duration_seconds": round(result.duration_seconds, 1),
            }
            (run_dir / "verdict.json").write_text(
                json.dumps(verdict, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )
            results.append(verdict)
            state = "PASS" if ok else "FAIL"
            print(
                f"[{index:02d}/{len(trigger.trigger_cases)}] {state} "
                f"expected={case.should_trigger} engaged={engaged} skill={skill_seen} "
                f"«{case.prompt}»",
                flush=True,
            )
    failures = [verdict for verdict in results if not verdict["ok"]]
    summary = {
        "trigger_set": args.trigger_set_id,
        "cases": len(results),
        "passed": len(results) - len(failures),
        "failed": len(failures),
        "model": config.model,
        "standards_revision": config.standards_revision,
        "failures": [{"prompt": item["prompt"], "note": item["note"]} for item in failures],
    }
    (reports_root / "summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"{summary['passed']}/{summary['cases']} passed — {reports_root}")
    return 0 if not failures else 1


def _render(worktree: Path, target: Path, revision: str) -> Path:
    from scripts.render import render_agents_md

    return render_agents_md(worktree, target, revision)


if __name__ == "__main__":
    sys.exit(main())
