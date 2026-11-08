"""CLI: the two-turn CP-008 invalidation scenario.

Turn 1 assesses a pass-worthy commit and records the report in the fixture.
The harness then moves the target head and extends the set (the harness may
mutate the fixture; the agent may not), re-anchors the branch heads, and turn
2 must re-resolve against the new state instead of reusing the stale verdict.
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import UTC, datetime
from pathlib import Path

from agents.kilo import KiloAdapter
from scorers import cherry_pick
from scripts.config import load_config
from scripts.fixtures import _git, _update_anchors, build_cp008
from scripts.git_utils import run_git
from scripts.standards import index_scenarios, resolve_standards_checkout

TURN2_PROMPT = (
    "цель обновилась (staging получил новый коммит, HEAD изменился), "
    "добавь к переносу ещё коммит BL-1001 из develop. "
    "Предыдущий отчёт оценки сохранён в файле turn-1-report.md в корне проекта."
)


def main(argv: list[str] | None = None) -> int:
    """Run both CP-008 turns; exit 1 when the invalidation discipline fails."""
    parser = argparse.ArgumentParser(description="Run the CP-008 two-turn scenario.")
    parser.add_argument("--config", type=Path, default=Path("config.toml"))
    parser.add_argument("--reports-dir", type=Path, default=Path("reports"))
    parser.add_argument(
        "--revision",
        type=str,
        default=None,
        help="Override the pinned standards revision (tag, branch, or commit)",
    )
    args = parser.parse_args(argv)

    config = load_config(args.config, args.revision)
    adapter = KiloAdapter(model=config.model, timeout_seconds=config.timeout_seconds)
    with resolve_standards_checkout(config) as worktree:
        scenario = index_scenarios(worktree)["CP-008"]
        reports_root = (args.reports_dir).resolve() / (
            f"{datetime.now(UTC).strftime('%Y%m%d-%H%M%S')}-CP-008"
        )
        run_dir = reports_root / "turns"
        run_dir.mkdir(parents=True, exist_ok=True)
        fixture = build_cp008(worktree, run_dir / "fixture", config.standards_revision, _render)
        original_heads = json.loads((fixture / "eval-anchors.json").read_text())

        turn1 = adapter.run(scenario.prompt, fixture, "CP-008-turn1")
        (run_dir / "turn-1-report.md").write_text(turn1.answer.strip(), encoding="utf-8")
        (run_dir / "turn-1-stdout.jsonl").write_text(turn1.stdout, encoding="utf-8")
        (fixture / "turn-1-report.md").write_text(turn1.answer.strip(), encoding="utf-8")

        # Harness-side target movement: staging advances on the same module and
        # the set gains BL-1001 on develop. Only slug.py is staged so harness
        # artifacts never leak into the fixture history. The agent stays
        # read-only.
        run_git(fixture, "checkout", "-q", "staging")
        slug = (fixture / "slug.py").read_text(encoding="utf-8")
        (fixture / "slug.py").write_text(
            slug.replace('"""URL slug helper."""', '"""URL slug helper (staging notes)."""'),
            encoding="utf-8",
        )
        _git(fixture, "add", "slug.py")
        _git(fixture, "commit", "-q", "-m", "chore: staging adjusts the slug module docstring")
        run_git(fixture, "checkout", "-q", "develop")
        _write_slug_v2(fixture)
        _git(fixture, "add", "-A")
        _git(fixture, "commit", "-q", "-m", "BL-1001: add separator option to slugify")
        _update_anchors(fixture)

        turn2 = adapter.run(TURN2_PROMPT, fixture, "CP-008-turn2")
        (run_dir / "turn-2-report.md").write_text(turn2.answer.strip(), encoding="utf-8")
        (run_dir / "turn-2-stdout.jsonl").write_text(turn2.stdout, encoding="utf-8")

        check = cherry_pick.check_cp008(turn2.answer.strip(), fixture)
        summary = {
            "scenario_id": "CP-008",
            "ok": check.ok,
            "failures": list(check.failures),
            "adapter": turn2.adapter,
            "model": config.model,
            "standards_revision": config.standards_revision,
            "original_heads": original_heads,
            "final_heads": json.loads((fixture / "eval-anchors.json").read_text()),
        }
        (reports_root / "summary.json").write_text(
            json.dumps(summary, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        # Set-level verdict in the release-report format.
        (reports_root / "verdict.json").write_text(
            json.dumps(
                {
                    "scenario_id": "CP-008",
                    "ok": check.ok,
                    "failures": list(check.failures),
                    "standards_revision": config.standards_revision,
                },
                ensure_ascii=False,
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )
        state = "PASS" if check.ok else "FAIL"
        print(f"CP-008 {state}: {check.failures or 'invalidation discipline held'}")
        print(f"artifacts: {reports_root}")
        return 0 if check.ok else 1


def _write_slug_v2(fixture: Path) -> None:
    slug = (fixture / "slug.py").read_text(encoding="utf-8")
    (fixture / "slug.py").write_text(
        slug.replace(
            "def slugify(text):",
            'def slugify(text, separator="-"):',
        ).replace(
            'return "-".join(text.lower().split())',
            "return separator.join(text.lower().split())",
        ),
        encoding="utf-8",
    )
    test = fixture / "tests" / "test_slug.py"
    test.write_text(
        test.read_text(encoding="utf-8")
        + '\n\n\ndef test_custom_separator():\n'
        + "    from slug import slugify\n"
        + '    assert slugify("Hello World", separator="_") == "hello_world"\n'
    )


def _render(worktree: Path, target: Path, revision: str) -> Path:
    from scripts.render import render_agents_md

    return render_agents_md(worktree, target, revision)


if __name__ == "__main__":
    sys.exit(main())
