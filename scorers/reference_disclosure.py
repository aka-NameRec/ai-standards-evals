"""Mechanical checks for the reference disclosure scenarios (RD-*).

The activation oracle reads the harness event stream: a scenario passes only
when the agent read the deployed reference file named by the pointer block
before doing the triggered work (RD-001), and — for the negative probe — when
unrelated work runs without any reference reads.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

from scorers.report_shape import ShapeCheck

_READ_TOOLS = frozenset({"read", "view", "cat"})
_WRITE_TOOLS = frozenset({"edit", "write", "apply_patch", "multiedit"})
_REFERENCE_HINT = ".ai-standards/references/"


def tool_events(stdout: str) -> list[dict[str, str]]:
    """Ordered ``(tool, path)`` pairs of tool_use events in a kilo JSONL stream.

    Non-JSON lines and events without a usable path are skipped; ordering
    follows the stream, which kilo emits chronologically.
    """
    events: list[dict[str, str]] = []
    for line in stdout.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        try:
            event = json.loads(stripped)
        except json.JSONDecodeError:
            continue
        if event.get("type") != "tool_use":
            continue
        part = event.get("part")
        if not isinstance(part, dict):
            continue
        tool = str(part.get("tool", "")).lower()
        state = part.get("state")
        payload: object = state if isinstance(state, dict) else part
        raw_input = payload.get("input") if isinstance(payload, dict) else None
        path = ""
        if isinstance(raw_input, dict):
            for key in ("filePath", "file_path", "path"):
                value = raw_input.get(key)
                if isinstance(value, str):
                    path = value
                    break
        events.append({"tool": tool, "path": path})
    return events


def _read_indices(events: list[dict[str, str]], substring: str) -> list[int]:
    return [
        index
        for index, event in enumerate(events)
        if event["tool"] in _READ_TOOLS and substring in event["path"]
    ]


def _first_edit_index(events: list[dict[str, str]]) -> int | None:
    return next(
        (index for index, event in enumerate(events) if event["tool"] in _WRITE_TOOLS),
        None,
    )


def _ok(failures: list[str]) -> ShapeCheck:
    return ShapeCheck(ok=not failures, failures=tuple(failures))


def reference_read_before_edit(stdout: str, reference_path: str) -> ShapeCheck:
    """RD-001 activation oracle: the reference was read, before any edit."""
    events = tool_events(stdout)
    reads = _read_indices(events, reference_path)
    if not reads:
        return _ok([
            f"harness trace shows no read of {reference_path}; "
            "the pointer block requires reading it before the triggered work"
        ])
    first_edit = _first_edit_index(events)
    if first_edit is not None and min(reads) > first_edit:
        return _ok([
            f"{reference_path} was read after the first edit; "
            "the reference must be read before the work starts"
        ])
    return _ok([])


def no_reference_reads(stdout: str) -> ShapeCheck:
    """RD-002 oracle: unrelated work reads no deployed reference files."""
    events = tool_events(stdout)
    stray = [
        event["path"]
        for event in events
        if event["tool"] in _READ_TOOLS and _REFERENCE_HINT in event["path"]
    ]
    if stray:
        return _ok([
            "unrelated task read reference files: " + ", ".join(sorted(set(stray)))
        ])
    return _ok([])


def _mentions(report: str, patterns: tuple[str, ...]) -> bool:
    return any(re.search(pattern, report, flags=re.IGNORECASE) for pattern in patterns)


def _reference_file(fixture_path: Path, relative: str) -> Path:
    # ``relative`` already starts with references/...; join under the managed
    # infrastructure directory.
    return fixture_path / ".ai-standards" / relative


def _read_reference_text(fixture_path: Path, relative: str) -> str:
    path = _reference_file(fixture_path, relative)
    if not path.is_file():
        return ""
    return path.read_text(encoding="utf-8")


def check_rd101(stdout: str, report: str, fixture_path: Path) -> ShapeCheck:
    failures: list[str] = []
    failures += reference_read_before_edit(stdout, "references/features/code-review.md").failures
    if "helper.py" not in report:
        failures.append("report does not name the reviewed defect file helper.py")
    if not _mentions(report, ("🔴", "🟡", "🔵")):
        failures.append("report carries no code-review severity markers")
    return _ok(failures)


def check_rd102(stdout: str, report: str, fixture_path: Path) -> ShapeCheck:
    failures: list[str] = []
    failures += reference_read_before_edit(stdout, "references/features/basic-memory.md").failures
    old_note = fixture_path / "docs" / "decisions" / "old-topic.md"
    new_note = fixture_path / "docs" / "decisions" / "new-topic.md"
    if old_note.exists():
        failures.append("old-topic.md still exists; the rename did not happen")
    if not new_note.exists():
        failures.append("new-topic.md is missing; the rename did not land")
    if new_note.exists():
        renamed = new_note.read_text(encoding="utf-8")
        if "relates_to" not in renamed and "Relations" not in renamed:
            failures.append("renamed note lost its Relations section")
    return _ok(failures)


def check_rd103(stdout: str, report: str, fixture_path: Path) -> ShapeCheck:
    failures: list[str] = []
    failures += reference_read_before_edit(stdout, "references/features/project-memory.md").failures
    if not _mentions(report, (r"backoff", r"retry", r"queue")):
        failures.append(
            "report does not reflect the seeded progress note (backoff/retry/queue)"
        )
    return _ok(failures)


def check_rd104(stdout: str, report: str, fixture_path: Path) -> ShapeCheck:
    failures: list[str] = []
    failures += reference_read_before_edit(stdout, "references/features/chroma.md").failures
    staleness = (r"stale", r"freshness", r"refresh", r"устар", r"обновит", r"обновлен")
    if not _mentions(report, staleness):
        failures.append(
            "report does not address the stale index (staleness/freshness gate)"
        )
    return _ok(failures)


def check_rd105(stdout: str, report: str, fixture_path: Path) -> ShapeCheck:
    failures: list[str] = []
    failures += reference_read_before_edit(
        stdout, "references/features/rule-engineering.md"
    ).failures
    flow_terms = (r"validat", r"валид", r"overlap", r"пересеч", r"unique", r"уник")
    if not _mentions(report, flow_terms):
        failures.append(
            "report does not name the engineering flow artifacts (validation, overlap)"
        )
    return _ok(failures)


def check_rd106(stdout: str, report: str, fixture_path: Path) -> ShapeCheck:
    failures: list[str] = []
    failures += reference_read_before_edit(
        stdout, "references/features/review-lenses.md"
    ).failures
    lens_terms = (r"reuse", r"quality", r"efficiency", r"переиспольз", r"качеств", r"эффектив")
    if not _mentions(report, lens_terms):
        failures.append("report does not structure the pass by the three lenses")
    return _ok(failures)


def check_rd107(stdout: str, report: str, fixture_path: Path) -> ShapeCheck:
    failures: list[str] = []
    failures += reference_read_before_edit(
        stdout, "references/features/knowledge-capture.md"
    ).failures
    decisions = {
        path
        for path in (fixture_path / "docs" / "decisions").glob("*.md")
        if path.name != ".gitkeep"
    }
    tasks = {
        path
        for path in (fixture_path / "docs" / "tasks").glob("*.md")
        if path.name != ".gitkeep"
    }
    if not decisions:
        failures.append("no decision record landed under docs/decisions/")
    if not tasks:
        failures.append("no task record landed under docs/tasks/")
    localized = any(
        (decision.parent / f"{decision.stem}.ru.md").exists() for decision in decisions
    )
    if decisions and not localized:
        failures.append("created decision record has no .ru.md pair")
    return _ok(failures)


def check_rd108(stdout: str, report: str, fixture_path: Path) -> ShapeCheck:
    failures: list[str] = []
    failures += reference_read_before_edit(
        stdout, "references/features/context-architecture.md"
    ).failures
    if not _mentions(
        report,
        (
            r"skill",
            r"retrieval",
            r"adapter",
            r"project knowledge",
            r"script",
            r"always[- ]loaded",
            r"скил",
            r"слой",
        ),
    ):
        failures.append("report does not name a placement layer from the model")
    return _ok(failures)


def check_rd110(stdout: str, report: str, fixture_path: Path) -> ShapeCheck:
    failures: list[str] = []
    failures += no_reference_reads(stdout).failures
    cli = fixture_path / "src" / "cli.py"
    if cli.exists() and "verbouse" in cli.read_text(encoding="utf-8"):
        failures.append("the verbose typo is still present in src/cli.py")
    if not report.strip():
        failures.append("agent produced no answer")
    return _ok(failures)


def check_rd111(stdout: str, report: str, fixture_path: Path) -> ShapeCheck:
    failures: list[str] = []
    failures += reference_read_before_edit(stdout, "references/features/code-review.md").failures
    failures += reference_read_before_edit(stdout, "references/stacks/django.md").failures
    violation = (r"orm", r"repository", r"репозитор", r"архитект", r"layer", r"сервис")
    if not _mentions(report, violation):
        failures.append(
            "report does not flag the direct-ORM-in-view architecture violation"
        )
    return _ok(failures)


def check_rd120_param(
    stdout: str,
    report: str,
    fixture_path: Path,
    stack: str,
    encoded_rule: str,
) -> ShapeCheck:
    failures: list[str] = []
    reference_relative = f"references/stacks/{stack}.md"
    failures += reference_read_before_edit(stdout, reference_relative).failures
    reference_text = _read_reference_text(fixture_path, relative=reference_relative)
    if reference_text and encoded_rule not in reference_text:
        failures.append(
            f"encoded rule {encoded_rule!r} is no longer part of the {stack} reference; "
            "the matrix parameter drifted from the standards"
        )
    applied = encoded_rule in report
    if not applied:
        src_dir = fixture_path / "src"
        probes = src_dir.rglob("*") if src_dir.exists() else []
        for probe in probes:
            if not probe.is_file():
                continue
            if encoded_rule in probe.read_text(encoding="utf-8", errors="ignore"):
                applied = True
                break
    if not applied:
        failures.append(
            f"the encoded {stack} rule ({encoded_rule!r}) is not observable in the "
            "answer or the edited probe file"
        )
    return _ok(failures)


RD_CHECKS = {
    "RD-101": check_rd101,
    "RD-102": check_rd102,
    "RD-103": check_rd103,
    "RD-104": check_rd104,
    "RD-105": check_rd105,
    "RD-106": check_rd106,
    "RD-107": check_rd107,
    "RD-108": check_rd108,
    "RD-110": check_rd110,
    "RD-111": check_rd111,
}
