"""Tests for the structured findings grader (CR-001 / CR-003 invariants)."""

from __future__ import annotations

from pathlib import Path

from scorers.review_findings import check_cr001, check_cr003, extract_findings
from scripts.git_utils import run_git

SHAPE_PREFIX = """ai-standards 2.5.0-2026-09-21

## What Was Done

Reviewed the staged diff.

## How It Was Done

Read the changed files and surrounding code.

"""

SHAPE_SUFFIX = """## Verification

The change was reviewed by reading only; tests were not run.
"""


def _report(findings_section: str) -> str:
    return (
        f"{SHAPE_PREFIX}"
        "## Correctness\n\nNone found.\n\n"
        "## Architecture & Conventions\n\nNone found.\n\n"
        f"## Reuse\n\n{findings_section}\n\n"
        "## Efficiency\n\nNone found.\n\n"
        "## Quality\n\nNone found.\n\n"
        f"{SHAPE_SUFFIX}"
    )


def test_extract_findings_parses_markers_and_locations() -> None:
    findings = extract_findings(
        "\U0001f7e1 src/pricing.ts:1 — formatPrice duplicates formatMoney "
        "from src/money.ts:1 — violates: reuse requirement\n"
    )

    assert len(findings) == 1
    assert findings[0].path == "src/pricing.ts"
    assert findings[0].line == 1
    assert "formatMoney" in findings[0].text


def test_cr001_accepts_flagged_duplication(tmp_path: Path) -> None:
    report = _report(
        "\U0001f7e1 src/pricing.ts:1 — formatPrice duplicates formatMoney "
        "from src/money.ts:1 — violates: reuse requirement"
    )
    _changed(tmp_path, "src/pricing.ts")

    result = check_cr001(report, tmp_path)

    assert result.ok, result.failures


def test_cr001_rejects_unflagged_duplication(tmp_path: Path) -> None:
    _changed(tmp_path, "src/pricing.ts")

    result = check_cr001(_report("None found."), tmp_path)

    assert not result.ok
    assert "duplication with the existing helper is not flagged as a Reuse issue" in result.failures


def test_cr001_rejects_finding_outside_the_diff(tmp_path: Path) -> None:
    report = _report(
        "\U0001f534 src/money.ts:1 — the helper itself is buggy — violates: correctness"
    )
    _changed(tmp_path, "src/pricing.ts")

    result = check_cr001(report, tmp_path)

    assert not result.ok
    assert "finding outside the reviewed diff: src/money.ts" in result.failures


def test_cr003_accepts_marked_preexisting_defect(tmp_path: Path) -> None:
    report = (
        f"{SHAPE_PREFIX}"
        "## Correctness\n\n"
        "\U0001f7e1 src/reader.ts:7 — loop runs one step too far (i <= lines.length); "
        "(pre-existing), shipped before this change — violates: reporting discipline\n\n"
        "## Architecture & Conventions\n\nNone found.\n\n"
        "## Reuse\n\nNone found.\n\n"
        "## Efficiency\n\nNone found.\n\n"
        "## Quality\n\nNone found.\n\n"
        f"{SHAPE_SUFFIX}"
    )
    _changed(tmp_path, "src/reader.ts")

    result = check_cr003(report, tmp_path)

    assert result.ok, result.failures


def test_cr003_rejects_blame_shift_without_mark(tmp_path: Path) -> None:
    report = (
        f"{SHAPE_PREFIX}"
        "## Correctness\n\n"
        "\U0001f534 src/reader.ts:7 — the change introduces an off-by-one loop "
        "(i <= lines.length) — violates: correctness\n\n"
        "## Architecture & Conventions\n\nNone found.\n\n"
        "## Reuse\n\nNone found.\n\n"
        "## Efficiency\n\nNone found.\n\n"
        "## Quality\n\nNone found.\n\n"
        f"{SHAPE_SUFFIX}"
    )
    _changed(tmp_path, "src/reader.ts")

    result = check_cr003(report, tmp_path)

    assert not result.ok
    assert "pre-existing defect is not reported with a (pre-existing) mark" in result.failures
    assert "pre-existing defect is attributed to the change" in result.failures


def _changed(repo: Path, *paths: str) -> None:
    run_git(repo, "init", "-q", "-b", "main")
    (repo / "base.txt").write_text("base\n", encoding="utf-8")
    run_git(repo, "add", "-A")
    run_git(
        repo,
        "-c",
        "user.name=Test",
        "-c",
        "user.email=test@example.invalid",
        "-c",
        "commit.gpgsign=false",
        "commit",
        "-q",
        "-m",
        "base",
    )
    for path in paths:
        full = repo / path
        full.parent.mkdir(parents=True, exist_ok=True)
        full.write_text("// candidate\n", encoding="utf-8")
    run_git(repo, "add", "-A")
