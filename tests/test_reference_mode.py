"""Tests for reference disclosure scorers and fixture builders (STD-CHANGE-0005)."""

from __future__ import annotations

import json
from pathlib import Path

from scorers.reference_disclosure import (
    check_rd101,
    check_rd110,
    check_rd111,
    check_rd120_param,
    no_reference_reads,
    reference_read_before_edit,
    tool_events,
)
from scripts.fixtures import (
    build_rd101,
    build_rd102,
    build_rd103,
    build_rd104,
    build_rd105,
    build_rd106,
    build_rd107,
    build_rd108,
    build_rd110,
    build_rd111,
)


def _event_stream(entries: list[tuple[str, str]]) -> str:
    lines = []
    for tool, path in entries:
        lines.append(
            json.dumps(
                {
                    "type": "tool_use",
                    "part": {
                        "tool": tool,
                        "state": {"status": "completed", "input": {"filePath": path}},
                    },
                }
            )
        )
    return "\n".join(lines)


READ_REF = (".ai-standards/references/features/code-review.md",)
EDIT = ("edit", "/fixture/src/stats.py")


def test_tool_events_parses_kilo_stream() -> None:
    stdout = _event_stream([("read", "/x/AGENTS.md"), ("edit", "/x/src/a.py")])
    events = tool_events(stdout)
    assert [event["tool"] for event in events] == ["read", "edit"]
    assert events[0]["path"] == "/x/AGENTS.md"


def test_reference_read_before_edit_detects_order() -> None:
    good = _event_stream([("read", "/f/" + READ_REF[0]), EDIT])
    bad = _event_stream([EDIT, ("read", "/f/" + READ_REF[0])])
    missing = _event_stream([EDIT])

    assert reference_read_before_edit(good, "references/features/code-review.md").ok
    assert not reference_read_before_edit(bad, "references/features/code-review.md").ok
    assert not reference_read_before_edit(missing, "references/features/code-review.md").ok


def test_no_reference_reads_flags_stray_reads() -> None:
    clean = _event_stream([("read", "/f/src/cli.py"), EDIT])
    stray = _event_stream([("read", "/f/.ai-standards/references/stacks/python.md")])

    assert no_reference_reads(clean).ok
    assert not no_reference_reads(stray).ok


def test_check_rd101_passes_compliant_run(tmp_path: Path) -> None:
    stdout = _event_stream([("read", "/f/.ai-standards/references/features/code-review.md")])
    report = "🟡 helper.py:7 — index out of range for p=100 — violates: correctness"

    check = check_rd101(stdout, report, tmp_path)

    assert check.ok, check.failures


def test_check_rd101_fails_without_reference_read(tmp_path: Path) -> None:
    stdout = _event_stream([("read", "/f/src/helper.py")])
    report = "🟡 helper.py:7 — off-by-one"

    check = check_rd101(stdout, report, tmp_path)

    assert not check.ok
    assert any("no read of" in failure for failure in check.failures)


def test_check_rd110_requires_no_stray_reads_and_the_fix(tmp_path: Path) -> None:
    cli = tmp_path / "src" / "cli.py"
    cli.parent.mkdir(parents=True)
    cli.write_text('print("--verbose: enable verbose logging")\n', encoding="utf-8")
    stdout = _event_stream([("read", "/f/src/cli.py"), EDIT])

    check = check_rd110(stdout, "Fixed the typo.", tmp_path)

    assert check.ok, check.failures

    cli.write_text('print("--verbose: enable verbouse logging")\n', encoding="utf-8")
    check = check_rd110(stdout, "Fixed the typo.", tmp_path)

    assert not check.ok


def test_check_rd111_requires_both_references(tmp_path: Path) -> None:
    both = _event_stream(
        [
            ("read", "/f/.ai-standards/references/features/code-review.md"),
            ("read", "/f/.ai-standards/references/stacks/django.md"),
        ]
    )
    report = "🔴 views.py:6 — direct ORM call in the view violates the layered stack rules"

    check = check_rd111(both, report, tmp_path)

    assert check.ok, check.failures

    one = _event_stream([("read", "/f/.ai-standards/references/features/code-review.md")])
    check = check_rd111(one, report, tmp_path)

    assert not check.ok


def test_check_rd120_param_encoded_rule_drift(tmp_path: Path) -> None:
    stdout = _event_stream([("read", "/f/.ai-standards/references/stacks/python.md")])
    reference = tmp_path / ".ai-standards" / "references" / "stacks"
    reference.mkdir(parents=True)
    (reference / "python.md").write_text(
        "- Prefer `pathlib.Path` over string paths.\n", encoding="utf-8"
    )
    report = "Использовал pathlib.Path по правилам стека."

    check = check_rd120_param(stdout, report, tmp_path, "python", "pathlib")

    assert check.ok, check.failures

    (reference / "python.md").write_text("- Rewritten reference body.\n", encoding="utf-8")
    check = check_rd120_param(stdout, report, tmp_path, "python", "pathlib")

    assert not check.ok
    assert any("drifted" in failure for failure in check.failures)


def _fake_render(worktree: Path, target: Path, revision: str) -> Path:
    rendered = target / "AGENTS.md"
    rendered.write_text("# stub AGENTS.md\n", encoding="utf-8")
    return rendered


def test_build_rd101_fixture_deploys_reference(tmp_path: Path, monkeypatch) -> None:
    synced: list[Path] = []

    def _fake_sync(worktree: Path, target: Path, revision: str) -> None:
        synced.append(target)

    monkeypatch.setattr("scripts.fixtures.sync_templates", _fake_sync)
    repo = build_rd101(tmp_path / "wt", tmp_path, "test-rev", _fake_render)

    assert synced == [repo]
    manifest = (repo / "ai.project.toml").read_text(encoding="utf-8")
    assert 'reference_features = ["code-review"]' in manifest
    staged = __import__("scripts.git_utils", fromlist=["run_git"]).run_git(
        repo, "diff", "--cached", "--name-only", "HEAD"
    )
    assert "helper.py" in staged
    assert "if not values:" in (repo / "helper.py").read_text(encoding="utf-8")


def test_build_rd102_fixture_seeded_rename_pair(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setattr(
        "scripts.fixtures.sync_templates",
        lambda worktree, target, revision: None,
    )
    repo = build_rd102(tmp_path / "wt", tmp_path, "test-rev", _fake_render)

    assert (repo / "docs" / "decisions" / "old-topic.md").is_file()
    content = (repo / "docs" / "decisions" / "old-topic.md").read_text(encoding="utf-8")
    assert "relates_to [[Related note]]" in content


def test_build_rd103_fixture_seeded_progress_marker(tmp_path: Path) -> None:
    repo = build_rd103(tmp_path / "wt", tmp_path, "test-rev", _fake_render)

    progress = (
        repo / "docs" / "local" / "progress" / "2026-11-01-checkout-service-progress.md"
    ).read_text(encoding="utf-8")
    assert "exponential backoff" in progress


def test_build_rd104_and_rd105_fixtures(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setattr(
        "scripts.fixtures.sync_templates",
        lambda worktree, target, revision: None,
    )
    stale = build_rd104(tmp_path / "wt", tmp_path, "test-rev", _fake_render)
    rules = build_rd105(tmp_path / "wt2", tmp_path, "test-rev", _fake_render)

    assert (stale / ".ai-standards" / "index-stale.marker").is_file()
    manifest = (stale / "ai.project.toml").read_text(encoding="utf-8")
    assert 'reference_features = ["chroma"]' in manifest
    assert 'reference_features = ["rule-engineering"]' in (rules / "ai.project.toml").read_text(
        encoding="utf-8"
    )
    assert (rules / "fragments" / "process" / "commit-lint.md").is_file()


def test_build_rd106_rd107_rd108_fixtures(tmp_path: Path) -> None:
    lenses = build_rd106(tmp_path / "wt", tmp_path, "test-rev", _fake_render)
    capture = build_rd107(tmp_path / "wt2", tmp_path, "test-rev", _fake_render)
    placement = build_rd108(tmp_path / "wt3", tmp_path, "test-rev", _fake_render)

    assert "blackFriday" in (lenses / "src" / "pricing.ts").read_text(encoding="utf-8")
    assert (capture / "docs" / "decisions" / ".gitkeep").is_file()
    assert (capture / "docs" / "tasks" / ".gitkeep").is_file()
    assert (placement / "proposals" / "framework-checklist.md").is_file()


def test_build_rd110_and_rd111_fixtures(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setattr(
        "scripts.fixtures.sync_templates",
        lambda worktree, target, revision: None,
    )
    negative = build_rd110(tmp_path / "wt", tmp_path, "test-rev", _fake_render)
    multi = build_rd111(tmp_path / "wt2", tmp_path, "test-rev", _fake_render)

    negative_manifest = (negative / "ai.project.toml").read_text(encoding="utf-8")
    assert 'reference_stacks = ["python"]' in negative_manifest
    assert "verbouse" in (negative / "src" / "cli.py").read_text(encoding="utf-8")

    multi_manifest = (multi / "ai.project.toml").read_text(encoding="utf-8")
    assert 'reference_features = ["code-review", "django"]' in multi_manifest
    staged = __import__("scripts.git_utils", fromlist=["run_git"]).run_git(
        multi, "diff", "--cached", "--name-only", "HEAD"
    )
    assert "orders/views.py" in staged
