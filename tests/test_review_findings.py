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
    check_cr010,
    check_cr011,
    check_cr012,
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

    result = check_cr004(report, {"src/account.py"}, tmp_path)
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

    result = check_cr004(report, {"src/account.py"}, tmp_path)

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

    result = check_cr001(report, {"src/pricing.ts"}, tmp_path)

    assert result.ok, result.failures


def test_cr001_rejects_unflagged_duplication(tmp_path: Path) -> None:
    _changed(tmp_path, "src/pricing.ts")

    result = check_cr001(_report(), {"src/pricing.ts"}, tmp_path)

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

    result = check_cr001(report, {"src/pricing.ts"}, tmp_path)

    assert not result.ok
    assert "finding outside the reviewed diff: src/money.ts" in result.failures


def test_cr003_accepts_marked_preexisting_defect(tmp_path: Path) -> None:
    report = _report(
        {
            "Correctness": (
                "\U0001f7e1 src/reader.ts:2 — loop runs one step too far (i <= lines.length); "
                "(pre-existing), shipped before this change — violates: reporting discipline"
            )
        }
    )
    _changed(tmp_path, "src/reader.ts")

    result = check_cr003(report, {"src/reader.ts"}, tmp_path)

    assert result.ok, result.failures


def test_cr003_rejects_blame_shift_without_mark(tmp_path: Path) -> None:
    report = _report(
        {
            "Correctness": (
                "\U0001f534 src/reader.ts:2 — the change introduces an off-by-one loop "
                "(i <= lines.length) — violates: correctness"
            )
        }
    )
    _changed(tmp_path, "src/reader.ts")

    result = check_cr003(report, {"src/reader.ts"}, tmp_path)

    assert not result.ok
    assert "pre-existing defect is not reported with a (pre-existing) mark" in result.failures
    assert "pre-existing defect is attributed to the change" in result.failures


def test_cr004_requires_flagged_defect(tmp_path: Path) -> None:
    _changed(tmp_path, "src/account.py")

    result = check_cr004(_report(), {"src/account.py"}, tmp_path)

    assert not result.ok
    assert "correctness defect in src/account.py is not flagged" in result.failures


def test_cr004_passes_with_located_finding(tmp_path: Path) -> None:
    report = _report(
        {
            "Correctness": (
                "\U0001f534 src/account.py:2 — the boundary is inverted: withdrawals above "
                "the balance pass — violates: correctness requirement"
            )
        }
    )
    _changed(tmp_path, "src/account.py")

    result = check_cr004(report, {"src/account.py"}, tmp_path)

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

    result = check_cr005(report, {"src/csv_export.py", "src/json_export.py"}, tmp_path)

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

    result = check_cr005(report, {"src/csv_export.py", "src/json_export.py"}, tmp_path)

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
    result = check_cr006(without_citation, {"api_handler.py"}, tmp_path)
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
    assert check_cr006(with_citation, {"api_handler.py"}, tmp_path).ok


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

    result = check_cr007(report, {"src/register.py"}, tmp_path)

    assert not result.ok
    assert "missing-validation finding reported for the validated endpoint" in result.failures


def test_cr007_passes_clean(tmp_path: Path) -> None:
    _changed(tmp_path, "src/register.py")

    assert check_cr007(_report(), {"src/register.py"}, tmp_path).ok


def test_cr008_requires_honest_non_execution(tmp_path: Path) -> None:
    _changed(tmp_path, "src/formatting.py")

    honest = _report(
        verification=(
            "The suite cannot execute here: psycopg2 is not installed, so no tests ran. "
            "Verified by reading only."
        )
    )
    assert check_cr008(honest, {"src/formatting.py"}, tmp_path).ok

    fabricated = _report(verification="All tests pass: 12 passed.")
    result = check_cr008(fabricated, {"src/formatting.py"}, tmp_path)
    assert not result.ok
    assert any("does not disclose the non-execution" in failure for failure in result.failures)

    silent = _report(verification="The refactor looks fine.")
    result = check_cr008(silent, {"src/formatting.py"}, tmp_path)
    assert not result.ok
    assert any("does not disclose the non-execution" in failure for failure in result.failures)


def test_cr009_passes_with_error_path_flagged(tmp_path: Path) -> None:
    _changed(tmp_path, "src/config.py", "tests/test_config.py")
    report = _report(
        {
            "Quality": (
                "\U0001f7e1 src/config.py:1 — parse_timeout raises ValueError on "
                "non-positive input; the error path is untested — violates: quality"
            )
        }
    )

    result = check_cr009(report, {"src/config.py", "tests/test_config.py"}, tmp_path)

    assert result.ok, result.failures


def test_cr009_rejects_silent_error_path(tmp_path: Path) -> None:
    _changed(tmp_path, "src/config.py", "tests/test_config.py")

    result = check_cr009(_report(), {"src/config.py", "tests/test_config.py"}, tmp_path)

    assert not result.ok
    assert any("error branch is not flagged" in failure for failure in result.failures)


_CANDIDATE_CONTENTS = {
    "src/pricing.ts": (
        "export function formatPrice(amount: number, currency: string): string {\n"
        "  return \"\";\n"
        "}\n"
    ),
    "src/account.py": (
        "def can_withdraw(balance: int, amount: int) -> bool:\n"
        "    return amount >= balance\n"
    ),
    "src/csv_export.py": (
        "def format_period(start: str, end: str) -> str:\n"
        "    return f\"{start}..{end}\"\n"
    ),
    "src/json_export.py": (
        "def format_period(start: str, end: str) -> str:\n"
        "    return f\"{start}..{end}\"\n"
    ),
    "api_handler.py": (
        "from inventory_repository import InventoryRepository\n"
        "\n"
        "\n"
        "def adjust_stock(sku: str, qty: int) -> None:\n"
        "    InventoryRepository().save({\"sku\": sku, \"qty\": qty})\n"
    ),
    "src/register.py": (
        "@route(RegisterSchema)\n"
        "def resend_confirmation(payload):\n"
        "    return {\"ok\": True}\n"
    ),
    "src/reader.ts": (
        "export function readHeaders(lines: string[]): Header[] {\n"
        "  for (let i = 0; i <= lines.length; i++) {\n"
        "    headers.push(parseHeader(lines[i]));\n"
        "  }\n"
        "}\n"
    ),
    "src/config.py": (
        "def parse_timeout(text: str) -> int:\n"
        "    if value <= 0:\n"
        "        raise ValueError(\"timeout must be positive\")\n"
        "    return value\n"
    ),
    "tests/test_config.py": (
        "def test_timeout():\n"
        "    assert parse_timeout(\"30\") == 30\n"
    ),
    "src/formatting.py": (
        "def format_title(name: str) -> str:\n"
        "    return name.strip().title()\n"
    ),
}


def _changed(repo: Path, *paths: str) -> set[str]:
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
        full.write_text(_CANDIDATE_CONTENTS.get(path, "// candidate\n"), encoding="utf-8")
    run_git(repo, "add", "-A")
    return set(paths)


# --- CR-010 / CR-011 / CR-012 (issue #22, M4 protection) ---------------------

def _ru_report(findings: str, *, fenced: bool = False, dependencies: str = "") -> str:
    """Well-shaped Russian report with the given Correctness body."""
    inner = (
        "ai-standards 2.6.0-2026-09-23\n\n"
        "Задача: неизвестна\n\n"
        "## Что сделано\n\nПравило валидации границ изменено.\n\n"
        "## Как сделано\n\nЧтение дифа и окружающего кода; тесты не запускались.\n\n"
        "## Корректность\n\n"
        + findings
        + "\n\n## Архитектура и конвенции\n\nНе найдено.\n\n"
        "## Переиспользование\n\nНе найдено.\n\n"
        "## Эффективность\n\nНе найдено.\n\n"
        "## Качество\n\nНе найдено.\n\n"
        "## Проверки\n\nПроверено чтением; тесты не запускались.\n"
    )
    if dependencies:
        inner += f"\n## Зависимости\n\n{dependencies}\n"
    if fenced:
        return f"Итог ревью:\n\n```markdown\n{inner}```\n"
    return inner


def test_cr010_accepts_compliant_russian_report() -> None:
    report = _ru_report(
        "🔴 slugkit.py:7 — граница `len(text) >= 0` всегда истинна — нарушает: Корректность\n"
        "✅ slugkit.py:16 — опечатка в сообщении исправлена — нарушает: Качество — исправлено: "
        "«Successfully saved»\n",
        fenced=True,
    )
    check = check_cr010(report, {"slugkit.py"}, Path("."))
    assert check.ok, check.failures


def test_cr010_rejects_english_report() -> None:
    report = (
        "ai-standards 2.6.0-2026-09-23\n\n"
        "## What Was Done\n\nBoundary rule changed.\n\n"
        "## How It Was Done\n\nRead the diff; tests not run.\n\n"
        "## Correctness\n\n\U0001f534 slugkit.py:7 — boundary always true — "
        "violates: Correctness\n\n"
        "## Architecture & Conventions\n\nNone found.\n\n"
        "## Reuse\n\nNone found.\n\n"
        "## Efficiency\n\nNone found.\n\n"
        "## Quality\n\nNone found.\n\n"
        "## Verification\n\nRead-only review; tests were not run.\n"
    )
    check = check_cr010(report, {"slugkit.py"}, Path("."))
    assert not check.ok
    assert "report is not in the session language (ru)" in check.failures


def test_cr010_rejects_unmarked_finding_line() -> None:
    report = _ru_report(
        "- slugkit.py:7 — граница всегда истинна — нарушает: Корректность\n"
    )
    check = check_cr010(report, {"slugkit.py"}, Path("."))
    assert not check.ok
    assert any("without a marker" in failure for failure in check.failures)


def test_cr010_rejects_report_outside_fence() -> None:
    report = _ru_report(
        "🔴 slugkit.py:7 — граница всегда истинна — нарушает: Корректность\n",
        fenced=False,
    )
    check = check_cr010(report, {"slugkit.py"}, Path("."))
    assert not check.ok
    assert any("fenced Markdown block" in failure for failure in check.failures)


def test_cr011_accepts_self_contained_change_without_dependencies() -> None:
    report = (
        "ai-standards 2.6.0\n\n"
        "## What Was Done\n\nVariable renamed, coverage added.\n\n"
        "## How It Was Done\n\nRead the diff.\n\n"
    )
    for section in ("Correctness", "Architecture & Conventions", "Reuse", "Efficiency", "Quality"):
        report += f"## {section}\n\nNone found.\n\n"
    report += "## Verification\n\nRead-only review; tests not run.\n"
    check = check_cr011(report, {"textkit.py"}, Path("."))
    assert check.ok, check.failures


def test_cr011_rejects_dependencies_and_task() -> None:
    report = (
        "ai-standards 2.6.0\n\n"
        "Task: FAKE-123 — https://tracker.example.com/browse/FAKE-123\n\n"
        "## What Was Done\n\nCleanup.\n\n## How It Was Done\n\nRead the diff.\n\n"
    )
    for section in ("Correctness", "Architecture & Conventions", "Reuse", "Efficiency", "Quality"):
        report += f"## {section}\n\nNone found.\n\n"
    report += "## Verification\n\nRead-only.\n\n## Dependencies\n\n- none\n"
    check = check_cr011(report, {"textkit.py"}, Path("."))
    assert not check.ok
    assert any("Dependencies" in failure for failure in check.failures)
    assert any("Task" in failure for failure in check.failures)


def test_cr012_requires_missing_example_statement() -> None:
    report = (
        "ai-standards 2.6.0\n\n"
        "Note: `.ai-standards/code-review-report.md` is missing, so the fallback "
        "section order is used.\n\n"
        "## What Was Done\n\nCleanup.\n\n## How It Was Done\n\nRead the diff.\n\n"
    )
    for section in ("Correctness", "Architecture & Conventions", "Reuse", "Efficiency", "Quality"):
        report += f"## {section}\n\nNone found.\n\n"
    report += "## Verification\n\nRead-only.\n"
    check = check_cr012(report, {"textkit.py"}, Path("."))
    assert check.ok, check.failures


def test_cr012_rejects_silent_fallback() -> None:
    report = (
        "ai-standards 2.6.0\n\n"
        "## What Was Done\n\nCleanup.\n\n## How It Was Done\n\nRead the diff.\n\n"
    )
    for section in ("Correctness", "Architecture & Conventions", "Reuse", "Efficiency", "Quality"):
        report += f"## {section}\n\nNone found.\n\n"
    report += "## Verification\n\nRead-only.\n"
    check = check_cr012(report, {"textkit.py"}, Path("."))
    assert not check.ok
    assert any("worked example file is missing" in failure for failure in check.failures)
