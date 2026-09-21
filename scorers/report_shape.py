"""Mechanical checks on the review report shape (RVW-015 and related rules).

The review report follows the chat language (RVW-022); harnesses may set Russian
as the chat language through global instructions, so both the English and the
Russian section vocabularies defined by the code-review fragment are accepted.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

FINDING_MARKERS = ("\U0001f534", "\U0001f7e1", "\U0001f535")

_VERSION_LINE = re.compile(r"(?im)^ai-standards\s+\S")
_VERSION_UNDETERMINED = re.compile(r"(?i)version is undetermined|версия не определена")
_HEADING = re.compile(r"^#{2,3}\s+(.+?)\s*$", re.MULTILINE)
_ANY_HEADING = re.compile(r"^#{2,3}\s+", re.MULTILINE)


@dataclass(frozen=True)
class _Locale:
    """Section vocabulary of one report language."""

    name: str
    required_sections: tuple[str, ...]
    prose_sections: tuple[str, ...]
    finding_sections: tuple[str, ...]
    honest_empty: str
    forbidden_heading: re.Pattern[str]


_LOCALE_EN = _Locale(
    name="en",
    required_sections=(
        "What Was Done",
        "How It Was Done",
        "Correctness",
        "Architecture & Conventions",
        "Reuse",
        "Efficiency",
        "Quality",
        "Verification",
    ),
    prose_sections=("What Was Done", "How It Was Done", "Verification"),
    finding_sections=(
        "Correctness",
        "Architecture & Conventions",
        "Reuse",
        "Efficiency",
        "Quality",
    ),
    honest_empty="None found.",
    forbidden_heading=re.compile(r"(?i)verdict|resolution"),
)

_LOCALE_RU = _Locale(
    name="ru",
    required_sections=(
        "Что сделано",
        "Как сделано",
        "Корректность",
        "Архитектура и конвенции",
        "Переиспользование",
        "Эффективность",
        "Качество",
        "Проверки",
    ),
    prose_sections=("Что сделано", "Как сделано", "Проверки"),
    finding_sections=(
        "Корректность",
        "Архитектура и конвенции",
        "Переиспользование",
        "Эффективность",
        "Качество",
    ),
    honest_empty="Не найдено.",
    forbidden_heading=re.compile(r"(?i)verdict|resolution|вердикт|итог|резолюция"),
)

_LOCALES = (_LOCALE_EN, _LOCALE_RU)


@dataclass(frozen=True)
class ShapeCheck:
    """Result of mechanical report checks; failures name each violated expectation."""

    ok: bool
    failures: tuple[str, ...]


def check(report: str) -> ShapeCheck:
    """Check the invariants every review report must satisfy."""
    locale = _select_locale(report)
    failures: list[str] = []
    headings = [match.group(1).strip() for match in _HEADING.finditer(report)]
    positions: list[int] = []
    for section in locale.required_sections:
        if section not in headings:
            failures.append(f"missing section: {section}")
        else:
            positions.append(headings.index(section))
    if positions != sorted(positions):
        failures.append("required sections are out of order")
    for heading in headings:
        if locale.forbidden_heading.search(heading):
            failures.append(f"forbidden heading: {heading}")
    if _VERSION_LINE.search(report) is None and _VERSION_UNDETERMINED.search(report) is None:
        failures.append("missing ai-standards version line or 'version is undetermined'")
    return ShapeCheck(ok=not failures, failures=tuple(failures))


def check_no_padding(report: str) -> ShapeCheck:
    """CR-002 control: clean change with honestly empty finding sections."""
    locale = _select_locale(report)
    base = check(report)
    failures = list(base.failures)
    for section in locale.finding_sections:
        body = _section_body(report, section)
        if not body.strip():
            failures.append(f"empty section body: {section}")
            continue
        for marker in FINDING_MARKERS:
            if marker in body:
                failures.append(f"manufactured finding in {section}")
        if locale.honest_empty not in body:
            failures.append(f"{section} does not state '{locale.honest_empty}' for a clean change")
    for section in locale.prose_sections:
        if not _section_body(report, section).strip():
            failures.append(f"empty section body: {section}")
    return ShapeCheck(ok=not failures, failures=tuple(failures))


def _select_locale(report: str) -> _Locale:
    """Pick the locale whose section vocabulary matches the report best."""
    headings = {match.group(1).strip() for match in _HEADING.finditer(report)}
    return max(
        _LOCALES,
        key=lambda locale: sum(section in headings for section in locale.required_sections),
    )


def _section_body(report: str, section: str) -> str:
    pattern = re.compile(rf"^#{{2,3}}\s+{re.escape(section)}\s*$", re.MULTILINE)
    match = pattern.search(report)
    if match is None:
        return ""
    next_heading = _ANY_HEADING.search(report, match.end())
    end = next_heading.start() if next_heading else len(report)
    return report[match.end() : end]
