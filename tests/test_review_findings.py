"""Tests for the structured findings grader (CR-001 / CR-003 invariants)."""

from __future__ import annotations

from pathlib import Path

from scorers.review_findings import (
    check_cr001,
    check_cr003,
    check_cr004,
    check_cr005,
    check_cr006,
    check_cr007,
    check_cr008,
    check_cr009,
    extract_findings,
)
from scripts.git_utils import run_git

SHAPE_PREFIX = """ai-standards 2.5.0-2026-09-21

## What Was Done

Reviewed the staged diff.

## How It Was Done

Read the changed files and surrounding code.

"""


def _report(overrides: dict[str, str] | None = None, verification: str | None = None) -> str:
    """Build a well-shaped report; `overrides` replaces per-section bodies."""
    overrides = overrides or {}
    parts = [SHAPE_PREFIX]
    for section in ("Correctness", "Architecture & Conventions", "Reuse", "Efficiency", "Quality"):
        parts.append(f"## {section}\n\n{overrides.get(section, 'None found.')}\n\n")
    parts.append(
        "## Verification\n\n"
        + (verification or "The change was reviewed by reading only. Tests were not run.")
        + "\n"
    )
    return "".join(parts)


def test_extract_findings_parses_markers_and_locations() -> None:
    findings = extract_findings(
        "\U0001f7e1 src/pricing.ts:1 — formatPrice duplicates formatMoney "
        "from src/money.ts:1 — violates: reuse requirement\n"
    )

    assert len(findings) == 1
    assert findings[0].path == "src/pricing.ts"
    assert findings[0].line == 1
    assert "formatMoney" in findings[0].text


def test_extract_findings_handles_list_bullets() -> None:
    findings = extract_findings(
        "- \U0001f534 src/account.py:6 — the operator is inverted — violates: correctness\n"
    )

    assert len(findings) == 1
    assert findings[0].path == "src/account.py"
    assert findings[0].marker == "\U0001f534"


def test_extract_findings_accepts_file_without_line(tmp_path: Path) -> None:
    report = _report(
        {
            "Quality": (
                "\U0001f535 conftest.py / repo root — empty conftest breaks collection "
                "(существовало ранее) — violates: completion discipline"
            )
        }
    )
    _changed(tmp_path, "src/account.py")

    findings = extract_findings(report)
    assert findings[0].path == "conftest.py"
    assert findings[0].line is None

    result = check_cr004(report, tmp_path)
    assert not any("without a file location" in failure for failure in result.failures)


def test_scope_allows_marked_preexisting_findings(tmp_path: Path) -> None:
    report = _report(
        {
            "Quality": (
                "\U0001f7e1 conftest.py:1 — pytest collection fails without PYTHONPATH "
                "(существовало ранее) — violates: completion discipline"
            )
        }
    )
    _changed(tmp_path, "src/account.py")

    result = check_cr004(report, tmp_path)

    assert not any("outside the reviewed diff" in failure for failure in result.failures)


def test_cr001_accepts_flagged_duplication(tmp_path: Path) -> None:
    report = _report(
        {
            "Reuse": (
                "\U0001f7e1 src/pricing.ts:1 — formatPrice duplicates formatMoney "
                "from src/money.ts:1 — violates: reuse requirement"
            )
        }
    )
    _changed(tmp_path, "src/pricing.ts")

    result = check_cr001(report, tmp_path)

    assert result.ok, result.failures


def test_cr001_rejects_unflagged_duplication(tmp_path: Path) -> None:
    _changed(tmp_path, "src/pricing.ts")

    result = check_cr001(_report(), tmp_path)

    assert not result.ok
    assert "duplication with the existing helper is not flagged as a Reuse issue" in result.failures


def test_cr001_rejects_finding_outside_the_diff(tmp_path: Path) -> None:
    report = _report(
        {
            "Reuse": (
                "\U0001f534 src/money.ts:1 — the helper itself is buggy — violates: correctness"
            )
        }
    )
    _changed(tmp_path, "src/pricing.ts")

    result = check_cr001(report, tmp_path)

    assert not result.ok
    assert "finding outside the reviewed diff: src/money.ts" in result.failures


def test_cr003_accepts_marked_preexisting_defect(tmp_path: Path) -> None:
    report = _report(
        {
            "Correctness": (
                "\U0001f7e1 src/reader.ts:7 — loop runs one step too far (i <= lines.length); "
                "(pre-existing), shipped before this change — violates: reporting discipline"
            )
        }
    )
    _changed(tmp_path, "src/reader.ts")

    result = check_cr003(report, tmp_path)

    assert result.ok, result.failures


def test_cr003_rejects_blame_shift_without_mark(tmp_path: Path) -> None:
    report = _report(
        {
            "Correctness": (
                "\U0001f534 src/reader.ts:7 — the change introduces an off-by-one loop "
                "(i <= lines.length) — violates: correctness"
            )
        }
    )
    _changed(tmp_path, "src/reader.ts")

    result = check_cr003(report, tmp_path)

    assert not result.ok
    assert "pre-existing defect is not reported with a (pre-existing) mark" in result.failures
    assert "pre-existing defect is attributed to the change" in result.failures


def test_cr004_requires_flagged_defect(tmp_path: Path) -> None:
    _changed(tmp_path, "src/account.py")

    result = check_cr004(_report(), tmp_path)

    assert not result.ok
    assert "correctness defect in src/account.py is not flagged" in result.failures


def test_cr004_passes_with_located_finding(tmp_path: Path) -> None:
    report = _report(
        {
            "Correctness": (
                "\U0001f534 src/account.py:7 — the boundary is inverted: withdrawals above "
                "the balance pass — violates: correctness requirement"
            )
        }
    )
    _changed(tmp_path, "src/account.py")

    result = check_cr004(report, tmp_path)

    assert result.ok, result.failures


def test_cr005_passes_with_flagged_internal_duplication(tmp_path: Path) -> None:
    _changed(tmp_path, "src/csv_export.py", "src/json_export.py")
    report = _report(
        {
            "Quality": (
                "\U0001f7e1 src/csv_export.py:3 — format_period duplicates "
                "src/json_export.py:3 — violates: DRY"
            )
        }
    )

    result = check_cr005(report, tmp_path)

    assert result.ok, result.failures


def test_cr005_rejects_invented_existing_helper_claim(tmp_path: Path) -> None:
    _changed(tmp_path, "src/csv_export.py", "src/json_export.py")
    report = _report(
        {
            "Reuse": (
                "\U0001f7e1 src/csv_export.py:3 — ignores the existing helper — "
                "violates: reuse"
            )
        }
    )

    result = check_cr005(report, tmp_path)

    assert not result.ok
    assert any("non-existent existing abstraction" in failure for failure in result.failures)


def test_cr006_requires_decision_citation(tmp_path: Path) -> None:
    _changed(tmp_path, "api_handler.py")

    without_citation = _report(
        {
            "Architecture & Conventions": (
                "\U0001f7e1 api_handler.py:6 — direct repository write is bad style — "
                "violates: layering"
            )
        }
    )
    result = check_cr006(without_citation, tmp_path)
    assert not result.ok
    assert "architecture finding does not cite the ADR-004 decision record" in result.failures

    with_citation = _report(
        {
            "Architecture & Conventions": (
                "\U0001f534 api_handler.py:6 — direct repository write conflicts with "
                "ADR-004; use InventoryReservationService — violates: accepted decision"
            )
        }
    )
    assert check_cr006(with_citation, tmp_path).ok


def test_cr007_rejects_missing_validation_finding(tmp_path: Path) -> None:
    _changed(tmp_path, "src/register.py")
    report = _report(
        {
            "Correctness": (
                "\U0001f534 src/register.py:40 — the new endpoint has no validation — "
                "violates: correctness"
            )
        }
    )

    result = check_cr007(report, tmp_path)

    assert not result.ok
    assert "missing-validation finding reported for the validated endpoint" in result.failures


def test_cr007_passes_clean(tmp_path: Path) -> None:
    _changed(tmp_path, "src/register.py")

    assert check_cr007(_report(), tmp_path).ok


def test_cr008_requires_honest_non_execution(tmp_path: Path) -> None:
    _changed(tmp_path, "src/formatting.py")

    honest = _report(
        verification=(
            "The suite cannot execute here: psycopg2 is not installed, so no tests ran. "
            "Verified by reading only."
        )
    )
    assert check_cr008(honest, tmp_path).ok

    fabricated = _report(verification="All tests pass: 12 passed.")
    result = check_cr008(fabricated, tmp_path)
    assert not result.ok
    assert any("claims successful test runs" in failure for failure in result.failures)

    silent = _report(verification="The refactor looks fine.")
    result = check_cr008(silent, tmp_path)
    assert not result.ok
    assert any("does not disclose the non-execution" in failure for failure in result.failures)


def test_cr009_passes_with_error_path_flagged(tmp_path: Path) -> None:
    _changed(tmp_path, "src/config.py", "tests/test_config.py")
    report = _report(
        {
            "Quality": (
                "\U0001f7e1 src/config.py:9 — parse_timeout raises ValueError on "
                "non-positive input; the error path is untested — violates: quality"
            )
        }
    )

    result = check_cr009(report, tmp_path)

    assert result.ok, result.failures


def test_cr009_rejects_silent_error_path(tmp_path: Path) -> None:
    _changed(tmp_path, "src/config.py", "tests/test_config.py")

    result = check_cr009(_report(), tmp_path)

    assert not result.ok
    assert any("error branch is not flagged" in failure for failure in result.failures)


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
