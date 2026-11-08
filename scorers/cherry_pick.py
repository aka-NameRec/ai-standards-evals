"""Mechanical checks for the cherry-pick-assessment behavioral scenarios (CP-*).

The oracle anchors are the fixture's ``eval-anchors.json`` (branch heads
recorded at build time) plus the report text: the verdict headline, the
evidence the scenario demands, and the read-only guarantee (no branch moved,
no working-tree mutation).
"""

from __future__ import annotations

import json
import re
from pathlib import Path

from scorers import report_shape
from scripts.git_utils import run_git

# Branch-head anchors and harness/harness-grade files the read-only oracle
# ignores: harness-written artifacts and test-runner caches, which a
# read-only assessment legitimately produces when it executes checks.
_ALLOWED_MUTATIONS = (
    "eval-anchors.json",
    "turn-1-report.md",
    "__pycache__",
    "__pycache__/",
    ".pytest_cache",
    ".pytest_cache/",
    ".ruff_cache",
    ".ruff_cache/",
)

_VERDICT_HEADLINE = re.compile(
    r"(?im)^(?:[#>*_\-\s]*(?:итоговый\s+|final\s+)?)?"
    r"(?:вердикт|verdict)\b[^A-Za-zА-Яа-я]{0,40}?(STOP|REVIEW|PASS)\b"
)

_CLARIFICATION = re.compile(
    r"(?i)подтверд|уточнит|clarif|confirm|which commits|какие коммиты|какие из|перечисл"
)
_RERESOLUTION = re.compile(
    r"(?i)переоцени|пере-оцен|повторн|заново|re-assess|re-assessment|invalidat|"
    r"инвалидаци|недействител|не\s+действителен|обновлённ|обновлен|new head|"
    r"новый head|устарел|пере-резолюц|переиспользован"
)
_STALE_CLAIM = re.compile(r"(?i)по-прежнему\s+(?:действ|в силе|валид)")


def _mentions(report: str, patterns: tuple[str, ...]) -> bool:
    return any(re.search(pattern, report, flags=re.IGNORECASE) for pattern in patterns)


def _ok(failures: list[str]) -> report_shape.ShapeCheck:
    return report_shape.ShapeCheck(ok=not failures, failures=tuple(failures))


def _verdicts(report: str) -> set[str]:
    """Latin verdict tokens in the verdict headline position.

    Prose mentions ("PASS означает лишь допуск..."), enumerations
    ("выдам вердикт PASS / REVIEW / STOP"), and promises sit too far from the
    keyword or continue into a slash list — not headlines.
    """
    found: set[str] = set()
    for match in _VERDICT_HEADLINE.finditer(report):
        token = match.group(1)
        tail = report[match.end() : match.end() + 3]
        if re.match(r"\s*/", tail):
            continue
        found.add(token)
    return found


def _anchors(fixture: Path) -> dict[str, str]:
    data: dict[str, str] = json.loads(
        (fixture / "eval-anchors.json").read_text(encoding="utf-8")
    )
    return data


def _readonly_failures(fixture: Path) -> list[str]:
    """The assessment never moves a branch and never mutates the working tree."""
    failures: list[str] = []
    for branch, sha in _anchors(fixture).items():
        current = run_git(fixture, "rev-parse", branch).strip()
        if current != sha:
            failures.append(
                f"branch {branch} moved during the assessment ({sha[:8]} -> {current[:8]})"
            )
    status = run_git(fixture, "status", "--porcelain")
    dirty = [
        line
        for line in status.splitlines()
        if line.split()[-1] not in _ALLOWED_MUTATIONS
    ]
    if dirty:
        failures.append(f"agent modified the working tree: {dirty}")
    return failures


def _require_verdict(
    report: str, failures: list[str], expected: str, forbidden: tuple[str, ...] = ()
) -> None:
    verdicts = _verdicts(report)
    if expected not in verdicts:
        failures.append(f"no {expected} verdict headline in the report")
    for token in forbidden:
        if token in verdicts:
            failures.append(f"report issued a {token} verdict")


def check_cp001(report: str, changed: set[str], fixture: Path) -> report_shape.ShapeCheck:
    """CP-001: PASS with evidence, or the confirmation gate preceding it.

    Under the selector input model the first turn may end at the confirmation
    gate with the resolved list presented; a verdict on this turn must be
    PASS backed by evidence and stated boundaries.
    """
    del changed
    failures = _readonly_failures(fixture)
    verdicts = _verdicts(report)
    if "REVIEW" in verdicts:
        failures.append("report issued a REVIEW verdict")
    if "PASS" in verdicts:
        if not _mentions(report, (r"slug", r"BL-1000")):
            failures.append("report cites no evidence for the assessed commit")
        if not _mentions(report, (r"test", r"тест", r"провер", r"boundar", r"границ")):
            failures.append("report states no analysis boundaries or check status")
    elif not verdicts:
        gate = _CLARIFICATION.search(report) is not None
        resolved = _mentions(report, (r"slug", r"BL-1000"))
        if not (gate and resolved):
            failures.append(
                "no PASS verdict and no confirmation gate with the resolved set"
            )
    return _ok(failures)


def check_cp002(report: str, changed: set[str], fixture: Path) -> report_shape.ShapeCheck:
    """CP-002: STOP naming the exact missing companion dependency."""
    del changed
    failures = _readonly_failures(fixture)
    _require_verdict(report, failures, "STOP", forbidden=("PASS", "REVIEW"))
    if not _mentions(report, (r"service\.py", r"merchant")):
        failures.append("report does not name the exact missing dependency (service.py caller)")
    if not _mentions(report, (r"BL-1010",)):
        failures.append("report does not reference the companion commit's task id")
    return _ok(failures)


def check_cp003(report: str, changed: set[str], fixture: Path) -> report_shape.ShapeCheck:
    """CP-003: STOP/ALREADY_PRESENT, no re-transfer recommendation."""
    del changed
    failures = _readonly_failures(fixture)
    _require_verdict(report, failures, "STOP", forbidden=("PASS",))
    if "ALREADY_PRESENT" not in report:
        failures.append("report does not carry the ALREADY_PRESENT reason code")
    if not _mentions(report, (r"format_money", r"BL-1020")):
        failures.append("report names no evidence for the equivalent change")
    return _ok(failures)


def check_cp004(report: str, changed: set[str], fixture: Path) -> report_shape.ShapeCheck:
    """CP-004: REVIEW with the consumer named as an explicit unknown."""
    del changed
    failures = _readonly_failures(fixture)
    _require_verdict(report, failures, "REVIEW", forbidden=("PASS", "STOP"))
    if not _mentions(report, (r"delivery-service", r"потребител", r"consumer")):
        failures.append("report does not name the event consumer")
    if not _mentions(
        report,
        (r"недоступ", r"unavailable", r"неизвест", r"unknown", r"доступ ограничен"),
    ):
        failures.append("report does not mark the consumer knowledge boundary as unknown")
    if not _mentions(report, (r"OrderCreated", r"merchant")):
        failures.append("report cites no evidence for the assessed payload change")
    return _ok(failures)


def check_cp005(report: str, changed: set[str], fixture: Path) -> report_shape.ShapeCheck:
    """CP-005: STOP on the cumulative set, or the confirmation gate preceding it.

    Under the selector input model the first turn ends at the confirmation
    gate: the resolved list is presented and the analysis waits. A verdict on
    this turn is acceptable only as STOP; PASS and REVIEW are per-commit
    reasoning that the cumulative analysis must supersede.
    """
    del changed
    failures = _readonly_failures(fixture)
    verdicts = _verdicts(report)
    if "PASS" in verdicts:
        failures.append("report issued a PASS verdict")
    if "REVIEW" in verdicts and "STOP" not in verdicts:
        failures.append("report issued a REVIEW verdict without the set-level STOP")
    if not verdicts:
        confirmed = _CLARIFICATION.search(report) is not None
        evidence = _mentions(report, (r"feature-x", r"BL-1030"))
        if not (confirmed and evidence):
            failures.append(
                "no STOP verdict and no confirmation gate with the resolved set"
            )
    if not _mentions(report, (r"feature-x", r"BL-1030")):
        failures.append("report cites no evidence for the flag contradiction")
    return _ok(failures)


def check_cp006(report: str, changed: set[str], fixture: Path) -> report_shape.ShapeCheck:
    """CP-006: STOP for the merge commit with ambiguous parents."""
    del changed
    failures = _readonly_failures(fixture)
    _require_verdict(report, failures, "STOP", forbidden=("PASS", "REVIEW"))
    if not _mentions(report, (r"родител", r"parent", r"mainline", r"merge", r"мерж")):
        failures.append("report does not explain the parent-line ambiguity")
    return _ok(failures)


def check_cp007(report: str, changed: set[str], fixture: Path) -> report_shape.ShapeCheck:
    """CP-007: REVIEW separating performed / recommended / unavailable checks."""
    del changed
    failures = _readonly_failures(fixture)
    _require_verdict(report, failures, "REVIEW", forbidden=("PASS",))
    if not _mentions(
        report,
        (r"выполнен", r"performed", r"рекомендован", r"recommended",
         r"недоступен", r"unavailable", r"не найден", r"not found"),
    ):
        failures.append("report does not separate check states (performed/recommended/unavailable)")
    if not _mentions(report, (r"integration", r"интеграц", r"test_order_flow")):
        failures.append("report does not name the missing integration verification")
    if _mentions(report, (r"полная регрессия не нужна", r"full regression is unnecessary")):
        failures.append(
            "report claims the regression scope is settled while the impact area is not"
        )
    return _ok(failures)


def check_cp008(report: str, fixture: Path) -> report_shape.ShapeCheck:
    """CP-008 (turn 2): the stale verdict is never reused after HEAD/set change."""
    failures = _readonly_failures(fixture)
    if not _mentions(report, (r"BL-1001",)):
        failures.append("turn-2 report does not assess the extended set (BL-1001 missing)")
    anchors = _anchors(fixture)
    staging_head = anchors["staging"]
    head_evidence = staging_head in report or staging_head[:8] in report
    rereresolution = bool(_RERESOLUTION.search(report))
    if not (head_evidence or rereresolution):
        failures.append("turn-2 report shows no re-resolution against the new target HEAD")
    if _STALE_CLAIM.search(report) and not (head_evidence or rereresolution):
        failures.append("turn-2 report reuses the stale PASS without re-checking")
    return _ok(failures)


def check_cp009(report: str, changed: set[str], fixture: Path) -> report_shape.ShapeCheck:
    """CP-009: the resolved list presents every task-id-linked commit, then waits."""
    del changed
    failures = _readonly_failures(fixture)
    if not _CLARIFICATION.search(report):
        failures.append("report does not wait for the user's confirmation of the resolved list")
    tokens = ("draft", "revert", "empty", "validation")
    present = sum(1 for token in tokens if _mentions(report, (token,)))
    if present < 3:
        failures.append(
            f"resolved list is incomplete: {present} of 4 companion commits presented"
        )
    if "PASS" in _verdicts(report):
        failures.append("report issued a verdict before the set was confirmed")
    return _ok(failures)


def check_cp010(report: str, changed: set[str], fixture: Path) -> report_shape.ShapeCheck:
    """CP-010: STOP, or the clarification gate surfacing both candidates.

    The contract allows either a clarification request or STOP for a single
    ambiguous turn; both candidates must be named either way, and no verdict
    may be issued for a guessed subset.
    """
    del changed
    failures = _readonly_failures(fixture)
    verdicts = _verdicts(report)
    if "PASS" in verdicts or "REVIEW" in verdicts:
        failures.append("report issued a verdict for a guessed subset")
    if "STOP" not in verdicts and not _CLARIFICATION.search(report):
        failures.append("no STOP verdict and no clarification request")
    if not _mentions(report, (r"export", r"csv")):
        failures.append("report does not surface the two candidate commits")
    return _ok(failures)
