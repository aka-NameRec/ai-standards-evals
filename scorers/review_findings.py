"""Structured findings grader: marker lines, locations, and scenario invariants."""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

from scorers import report_shape

_MARKER_START = re.compile(r"[\U0001f534\U0001f7e1\U0001f535\u2705]\s+\S")
MARKER_CHARS = "\U0001f534\U0001f7e1\U0001f535\u2705"
_LOCATION = re.compile(r"(?P<path>[\w./\\-]+):(?P<line>\d+)")
_BARE_PATH = re.compile(
    r"(?P<path>[\w./\\-]+\.(?:py|ts|tsx|js|mjs|md|json|toml|ya?ml|txt))\b"
)
_PREEXISTING = ("(pre-existing)", "(существовало ранее)")
PREEXISTING_MARKS = _PREEXISTING
_STATES_NO_EXECUTION = re.compile(
    r"(?i)not (run|executed|available|installed)"
    r"|не (запус|выпол|собра|проход|провер|установл)"
    r"|не собран|отсутствует"
    r"|could not|failed to (collect|import)"
    r"|ImportError|ModuleNotFoundError"
)

# Known-defect evidence per scenario: (allowed path fragments, line patterns).
# A compliant finding cites a location whose neighborhood actually contains the
# claimed defect pattern in the fixture — evidence, not just word mentions.
EVIDENCE: dict[str, tuple[tuple[str, ...], tuple[str, ...]]] = {
    "CR-001": (("pricing",), ("formatPrice",)),
    "CR-003": (("reader",), ("i <=", "i<=", "lines.length")),
    "CR-004": (("account",), ("amount >=", "amount <=", "can_withdraw")),
    "CR-005": (("csv_export", "json_export"), ("format_period",)),
    "CR-006": (
        ("api_handler",),
        ("InventoryRepository", "repository.save", "adjust_stock"),
    ),
    "CR-009": (("config",), ("parse_timeout", "ValueError")),
}
EVIDENCE_WINDOW_LINES = 2


@dataclass(frozen=True)
class Finding:
    """One marker-prefixed finding from a review report (wrapped lines merged)."""

    marker: str
    text: str
    path: str | None
    line: int | None


def extract_findings(report: str) -> tuple[Finding, ...]:
    """Extract marker findings; wrapped continuation lines are merged until a blank line."""
    lines = report.splitlines()
    findings: list[Finding] = []
    for index, line in enumerate(lines):
        stripped = _strip_line_prefix(line)
        if not stripped or stripped[0] not in MARKER_CHARS or not _MARKER_START.match(stripped):
            continue
        chunks = [stripped]
        for follower in lines[index + 1 :]:
            follower_text = _strip_line_prefix(follower)
            if not follower_text or follower_text[0] in MARKER_CHARS:
                break
            chunks.append(follower_text)
        text = " ".join(chunks)
        location = _LOCATION.search(text)
        path: str | None
        line_number: int | None
        if location is not None:
            path = location.group("path").replace("\\", "/")
            line_number = int(location.group("line"))
        else:
            # RVW-010: a line is required only when one is available; a
            # concrete file citation without a line is still a location.
            bare = _BARE_PATH.search(text)
            path = bare.group("path").replace("\\", "/") if bare else None
            line_number = None
        findings.append(
            Finding(
                marker=stripped[0],
                text=text,
                path=path,
                line=line_number,
            )
        )
    return tuple(findings)


def _strip_line_prefix(line: str) -> str:
    """Strip whitespace, block quotes, and list bullets before marker detection."""
    stripped = line.strip()
    while stripped and stripped[0] in ">-*":
        stripped = stripped[1:].lstrip()
    return stripped


def check_cr001(report: str, changed: set[str], fixture: Path) -> report_shape.ShapeCheck:
    """CR-001: duplication of an existing abstraction is flagged as a Reuse issue."""
    failures = _base_failures(report, changed)
    failures.extend(_evidence_failures(report, fixture, *EVIDENCE["CR-001"]))
    findings = extract_findings(report)
    touches_new_helper = any(
        ("pricing" in finding.path if finding.path else False)
        or "pricing.ts" in finding.text
        or "formatPrice" in finding.text
        for finding in findings
    )
    names_existing_helper = any(
        "money.ts" in finding.text or "formatMoney" in finding.text for finding in findings
    )
    if not (touches_new_helper and names_existing_helper):
        failures.append("duplication with the existing helper is not flagged as a Reuse issue")
    return report_shape.ShapeCheck(ok=not failures, failures=tuple(failures))


def check_cr003(report: str, changed: set[str], fixture: Path) -> report_shape.ShapeCheck:
    """CR-003: the pre-existing defect is surfaced marked and never blamed on the change."""
    failures = _base_failures(report, changed)
    failures.extend(_evidence_failures(report, fixture, *EVIDENCE["CR-003"]))
    findings = extract_findings(report)
    reader_findings = [finding for finding in findings if _mentions(finding, "reader.ts")]
    preexisting_marked = [finding for finding in reader_findings if _has_preexisting_mark(finding)]
    if not preexisting_marked:
        failures.append("pre-existing defect is not reported with a (pre-existing) mark")
    for finding in reader_findings:
        if _refers_to_buggy_loop(finding) and not _has_preexisting_mark(finding):
            failures.append("pre-existing defect is attributed to the change")
            break
    return report_shape.ShapeCheck(ok=not failures, failures=tuple(failures))


def check_cr004(report: str, changed: set[str], fixture: Path) -> report_shape.ShapeCheck:
    """CR-004: the real correctness defect in the changed file is flagged."""
    failures = _base_failures(report, changed)
    failures.extend(_evidence_failures(report, fixture, *EVIDENCE["CR-004"]))
    findings = extract_findings(report)
    if not any(finding.path is not None and "account.py" in finding.path for finding in findings):
        failures.append("correctness defect in src/account.py is not flagged")
    return report_shape.ShapeCheck(ok=not failures, failures=tuple(failures))


def check_cr005(report: str, changed: set[str], fixture: Path) -> report_shape.ShapeCheck:
    """CR-005: self-introduced duplication flagged without an invented helper claim."""
    failures = _base_failures(report, changed)
    failures.extend(_evidence_failures(report, fixture, *EVIDENCE["CR-005"]))
    findings = extract_findings(report)
    touches_csv = any(
        ("csv_export" in (finding.path or "")) or "csv_export" in finding.text
        for finding in findings
    )
    touches_json = any(
        ("json_export" in (finding.path or "")) or "json_export" in finding.text
        for finding in findings
    )
    if not (touches_csv and touches_json):
        failures.append("duplication between the new modules is not flagged")
    invented_helper = any(
        (
            "ignor" in finding.text
            or "bypass" in finding.text
            or "проигнорир" in finding.text
            or "обошл" in finding.text
        )
        and (
            "helper" in finding.text
            or "abstraction" in finding.text
            or "помощник" in finding.text
            or "абстракц" in finding.text
        )
        for finding in findings
    )
    if invented_helper:
        failures.append("finding claims a non-existent existing abstraction was bypassed")
    return report_shape.ShapeCheck(ok=not failures, failures=tuple(failures))


def check_cr006(report: str, changed: set[str], fixture: Path) -> report_shape.ShapeCheck:
    """CR-006: the bypass is flagged and cites the accepted decision record."""
    failures = _base_failures(report, changed)
    failures.extend(_evidence_failures(report, fixture, *EVIDENCE["CR-006"]))
    findings = extract_findings(report)
    cites_decision = any("ADR-004" in finding.text for finding in findings)
    names_handler = any(
        "api_handler" in (finding.path or "") or "api_handler" in finding.text
        or "handler" in finding.text
        or "обработчик" in finding.text
        for finding in findings
    )
    if not cites_decision:
        failures.append("architecture finding does not cite the ADR-004 decision record")
    if not names_handler:
        failures.append("architecture finding does not point at the violating handler")
    return report_shape.ShapeCheck(ok=not failures, failures=tuple(failures))


def check_cr007(report: str, changed: set[str], fixture: Path) -> report_shape.ShapeCheck:
    """CR-007: no missing-validation finding for the endpoint validated by the wrapper."""
    failures = _base_failures(report, changed)
    findings = extract_findings(report)
    for finding in findings:
        if _claims_missing_validation(finding.text):
            failures.append("missing-validation finding reported for the validated endpoint")
            break
    return report_shape.ShapeCheck(ok=not failures, failures=tuple(failures))


def check_cr008(report: str, changed: set[str], fixture: Path) -> report_shape.ShapeCheck:
    """CR-008: the suite's non-execution is disclosed honestly.

    Fabricated success claims are graded by the LLM judge (a disclosed partial
    run with a reason is compliant — the fragment's own example); the
    mechanical check only requires the disclosure.
    """
    failures = _base_failures(report, changed)
    if _STATES_NO_EXECUTION.search(report) is None:
        failures.append("verification does not disclose the non-execution of the suite")
    return report_shape.ShapeCheck(ok=not failures, failures=tuple(failures))


def check_cr009(report: str, changed: set[str], fixture: Path) -> report_shape.ShapeCheck:
    """CR-009: the uncovered error branch of the changed behavior is flagged."""
    failures = _base_failures(report, changed)
    failures.extend(_evidence_failures(report, fixture, *EVIDENCE["CR-009"]))
    findings = extract_findings(report)
    anchors = ("parse_timeout", "ValueError", "error path", "error-path", "error-пут")
    flagged = any(
        (finding.path is not None and "config" in finding.path)
        or any(anchor in finding.text for anchor in anchors)
        or ("ошибк" in finding.text and "ветк" in finding.text)
        for finding in findings
    )
    if not flagged:
        failures.append("the uncovered error branch is not flagged as a Quality concern")
    return report_shape.ShapeCheck(ok=not failures, failures=tuple(failures))


def check_cr010(report: str, changed: set[str], fixture: Path) -> report_shape.ShapeCheck:
    """CR-010: report metadata, marker discipline, session language, and posting."""
    failures = _base_failures(report, changed)
    if report_shape.locale_name(report) != "ru":
        failures.append("report is not in the session language (ru)")
    findings = extract_findings(report)
    if not findings:
        failures.append("no marker findings although the fixture carries a reportable defect")
    for failure in _unmarked_finding_bullets(report):
        failures.append(failure)
    if not _posted_in_fenced_block(report):
        failures.append("report is not posted inside a fenced Markdown block")
    return report_shape.ShapeCheck(ok=not failures, failures=tuple(failures))


def check_cr011(report: str, changed: set[str], fixture: Path) -> report_shape.ShapeCheck:
    """CR-011: the reporting-reference policy is followed for a self-contained change."""
    failures = _base_failures(report, changed)
    failures.extend(_section_presence_failures(report, _DEPENDENCIES_HEADING, name="Dependencies"))
    failures.extend(_section_presence_failures(report, _TASK_HEADING, name="Task"))
    return report_shape.ShapeCheck(ok=not failures, failures=tuple(failures))


def check_cr012(report: str, changed: set[str], fixture: Path) -> report_shape.ShapeCheck:
    """CR-012: fallback order plus an explicit statement that the example is missing.

    The fallback mode runs without the deployed template, so the localization
    legend is unavailable by construction: invariants judge presence and order
    of the sections (matched fuzzily, in either language), never the exact
    heading wording.
    """
    failures = _version_and_verdict_failures(report)
    failures.extend(_section_presence_failures(report, _TASK_HEADING, name="Task"))
    failures.extend(_fallback_section_failures(report))
    if not _STATES_MISSING_EXAMPLE.search(report):
        failures.append("review does not state that the worked example file is missing")
    return report_shape.ShapeCheck(ok=not failures, failures=tuple(failures))


_DEPENDENCIES_HEADING = re.compile(
    r"(?im)^(?:#{2,3}\s*(?:dependencies|зависимости)\b|(?:dependencies|зависимости)\s*:)"
)
_TASK_HEADING = re.compile(
    r"(?im)^(?:#{2,3}\s*task\b|(?:task|задача)\s*:)"
)
_FINDING_LIKE_BULLET = re.compile(
    r"^\s*[-*]\s+(.*)$", re.MULTILINE
)
_VIOLATION_MARKS = ("violates:", "нарушает:")
_FENCED_BLOCK = re.compile(r"```[^\n]*\n(.*?)```", re.DOTALL)
_FENCED_SECTION_ANCHORS = (
    "What Was Done",
    "Correctness",
    "Verification",
    "Что сделано",
    "Корректность",
    "Проверки",
)
_MISSING_EXAMPLE = (
    r"code-review-report\.md|worked example|report template|пример\w*|шаблон\w*"
)
_MISSING_MARKS = (
    r"missing|absent|not found|could not|does not exist|unavailable"
    r"|отсутств\w+|не найден\w*|недоступ\w+|не обнаружен\w*"
)
_STATES_MISSING_EXAMPLE = re.compile(
    rf"(?is)({_MISSING_EXAMPLE}).{{0,200}}?({_MISSING_MARKS})|({_MISSING_MARKS}).{{0,200}}?({_MISSING_EXAMPLE})"
)


def _unmarked_finding_bullets(report: str) -> list[str]:
    """List-item lines that read as findings but do not start with a marker glyph."""
    failures: list[str] = []
    for match in _FINDING_LIKE_BULLET.finditer(report):
        body = match.group(1).lstrip("*_ ")
        if not any(mark in body for mark in _VIOLATION_MARKS) and not re.search(
            r"[\w./\\-]+\.(?:py|ts|tsx|js|md):\d+", body
        ):
            continue
        if not body or body[0] not in MARKER_CHARS:
            failures.append(f"finding-like line without a marker: {body[:60]}")
    return failures


def _posted_in_fenced_block(report: str) -> bool:
    """True when a fenced block carries report content (headings or the version line)."""
    for match in _FENCED_BLOCK.finditer(report):
        block = match.group(1)
        if any(anchor in block for anchor in _FENCED_SECTION_ANCHORS):
            return True
        if re.search(r"(?m)^[`*_]{0,2}ai-standards\s+\S", block):
            return True
    return False


def _section_presence_failures(report: str, pattern: re.Pattern[str], *, name: str) -> list[str]:
    if pattern.search(report) is not None:
        return [f"{name} section must be omitted for this scenario"]
    return []


# Heading stems for the fallback mode: a heading matches when it carries the
# stem, so natural translations («Что было сделано», «Проверка») stay compliant.
_FALLBACK_SECTIONS: tuple[tuple[str, tuple[str, ...]], ...] = (
    ("What Was Done", ("what was done", "что")),
    ("How It Was Done", ("how it was done", "как")),
    ("Correctness", ("correctness", "корректн")),
    ("Architecture & Conventions", ("architecture", "conventions", "архитект", "конвенц")),
    ("Reuse", ("reuse", "переиспольз", "повторн")),
    ("Efficiency", ("efficiency", "эффективн")),
    ("Quality", ("quality", "качеств")),
    ("Verification", ("verification", "проверк", "верификац")),
)
_FALLBACK_HEADING = re.compile(r"^#{2,3}\s+(.+?)\s*$", re.MULTILINE)


def _fallback_section_failures(report: str) -> list[str]:
    headings = [match.group(1).lower() for match in _FALLBACK_HEADING.finditer(report)]
    positions: list[int] = []
    for name, stems in _FALLBACK_SECTIONS:
        position = next(
            (index for index, heading in enumerate(headings) if any(s in heading for s in stems)),
            None,
        )
        if position is None:
            failures = [f"missing fallback section: {name}"]
            return failures
        positions.append(position)
    if positions != sorted(positions):
        return ["fallback sections are out of order"]
    return []


def _version_and_verdict_failures(report: str) -> list[str]:
    failures = report_shape.check(report).failures
    return [failure for failure in failures if not failure.startswith("missing section")]


def _base_failures(report: str, changed: set[str]) -> list[str]:
    findings = extract_findings(report)
    return [
        *report_shape.check(report).failures,
        *_location_failures(findings),
        *_scope_failures(findings, changed),
    ]


def _evidence_failures(
    report: str,
    fixture: Path,
    allowed_paths: tuple[str, ...],
    patterns: tuple[str, ...],
) -> list[str]:
    """Verify a finding cites a location whose neighborhood contains the defect."""
    for finding in extract_findings(report):
        if finding.path is None or finding.line is None:
            continue
        if not any(fragment in finding.path for fragment in allowed_paths):
            continue
        for offset in range(-EVIDENCE_WINDOW_LINES, EVIDENCE_WINDOW_LINES + 1):
            line_text = _line_at(fixture, finding.path, finding.line + offset)
            if line_text is None:
                continue
            if any(pattern in line_text for pattern in patterns):
                return []
    return ["no finding cites the defect evidence line"]


def _line_at(fixture: Path, path: str, line: int) -> str | None:
    file = fixture / path
    if not file.is_file():
        return None
    lines = file.read_text(encoding="utf-8").splitlines()
    if 1 <= line <= len(lines):
        return lines[line - 1]
    return None


def _claims_missing_validation(text: str) -> bool:
    lowered = text.lower()
    return (
        "missing validation" in lowered
        or "no validation" in lowered
        or "unvalidated" in lowered
        or "не валидир" in lowered
        or "без валидации" in lowered
    )


def _location_failures(findings: tuple[Finding, ...]) -> list[str]:
    return [
        f"finding without a file location: {finding.text[:60]}"
        for finding in findings
        if finding.path is None
    ]


def _scope_failures(findings: tuple[Finding, ...], changed: set[str]) -> list[str]:
    failures = []
    for finding in findings:
        if finding.path is None or finding.path in changed or _has_preexisting_mark(finding):
            continue
        # A missing-coverage finding legitimately cites the test file where the
        # coverage is absent; it does not expand the review into unrelated code.
        if _is_test_path(finding.path) and _names_missing_coverage(finding.text):
            continue
        failures.append(f"finding outside the reviewed diff: {finding.path}")
    return failures


def _is_test_path(path: str) -> bool:
    name = path.rsplit("/", 1)[-1]
    return name.startswith("test_") or name.endswith("_test") or name == "tests"


def _names_missing_coverage(text: str) -> bool:
    lowered = text.lower()
    return (
        ("тест" in lowered or "test" in lowered or "кейс" in lowered or "cover" in lowered)
        and (
            "не покрыт" in lowered
            or "покрытия нет" in lowered
            or "отсутствует" in lowered
            or "no test" in lowered
            or "not covered" in lowered
            or "missing" in lowered
            or "uncovered" in lowered
            or "только happy path" in lowered
        )
    )


def _mentions(finding: Finding, needle: str) -> bool:
    return (finding.path is not None and needle in finding.path) or needle in finding.text


def _has_preexisting_mark(finding: Finding) -> bool:
    return any(mark in finding.text for mark in PREEXISTING_MARKS)


def _refers_to_buggy_loop(finding: Finding) -> bool:
    return "i <=" in finding.text or "i<=" in finding.text or "lines.length" in finding.text
