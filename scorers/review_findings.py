"""Structured findings grader: marker lines, locations, and scenario invariants."""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

from scorers import report_shape
from scripts.oracle import changed_files

_MARKER_START = re.compile(r"[\U0001f534\U0001f7e1\U0001f535\u2705]\s+\S")
MARKER_CHARS = "\U0001f534\U0001f7e1\U0001f535\u2705"
_LOCATION = re.compile(r"(?P<path>[\w./\\-]+):(?P<line>\d+)")
PREEXISTING_MARKS = ("(pre-existing)", "(существовало ранее)")


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
        stripped = line.strip().lstrip(">").strip()
        if not stripped or stripped[0] not in MARKER_CHARS or not _MARKER_START.match(stripped):
            continue
        chunks = [stripped]
        for follower in lines[index + 1 :]:
            follower_text = follower.strip().lstrip(">").strip()
            if not follower_text or follower_text[0] in MARKER_CHARS:
                break
            chunks.append(follower_text)
        text = " ".join(chunks)
        location = _LOCATION.search(text)
        findings.append(
            Finding(
                marker=stripped[0],
                text=text,
                path=location.group("path").replace("\\", "/") if location else None,
                line=int(location.group("line")) if location else None,
            )
        )
    return tuple(findings)


def check_cr001(report: str, fixture: Path) -> report_shape.ShapeCheck:
    """CR-001: duplication of an existing abstraction is flagged as a Reuse issue."""
    failures = list(report_shape.check(report).failures)
    findings = extract_findings(report)
    failures.extend(_location_failures(findings))
    failures.extend(_scope_failures(findings, fixture))
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


def check_cr003(report: str, fixture: Path) -> report_shape.ShapeCheck:
    """CR-003: the pre-existing defect is surfaced marked and never blamed on the change."""
    failures = list(report_shape.check(report).failures)
    findings = extract_findings(report)
    failures.extend(_location_failures(findings))
    failures.extend(_scope_failures(findings, fixture))
    reader_findings = [
        finding for finding in findings if _mentions(finding, "reader.ts")
    ]
    preexisting_marked = [
        finding for finding in reader_findings if _has_preexisting_mark(finding)
    ]
    if not preexisting_marked:
        failures.append("pre-existing defect is not reported with a (pre-existing) mark")
    for finding in reader_findings:
        if _refers_to_buggy_loop(finding) and not _has_preexisting_mark(finding):
            failures.append("pre-existing defect is attributed to the change")
            break
    return report_shape.ShapeCheck(ok=not failures, failures=tuple(failures))


def _location_failures(findings: tuple[Finding, ...]) -> list[str]:
    return [
        f"finding without a file location: {finding.text[:60]}"
        for finding in findings
        if finding.path is None
    ]


def _scope_failures(findings: tuple[Finding, ...], fixture: Path) -> list[str]:
    changed = changed_files(fixture)
    return [
        f"finding outside the reviewed diff: {finding.path}"
        for finding in findings
        if finding.path is not None and finding.path not in changed
    ]


def _mentions(finding: Finding, needle: str) -> bool:
    return (finding.path is not None and needle in finding.path) or needle in finding.text


def _has_preexisting_mark(finding: Finding) -> bool:
    return any(mark in finding.text for mark in PREEXISTING_MARKS)


def _refers_to_buggy_loop(finding: Finding) -> bool:
    return "i <=" in finding.text or "i<=" in finding.text or "lines.length" in finding.text
