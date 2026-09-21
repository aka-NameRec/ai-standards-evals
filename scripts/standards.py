"""Standards-side interface: pinned checkout, rule map, and scenario contracts."""

from __future__ import annotations

import re
import tempfile
import tomllib
from collections.abc import Iterator
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
from typing import cast

from scripts.config import EvalConfig
from scripts.git_utils import run_git

KIND_BEHAVIOR = "behavior"
KIND_TRIGGER_SET = "trigger_set"

_SCENARIO_FILE = re.compile(r"^([A-Z]{2,}-\d{3})-.+\.md\Z")
_ID_REFERENCE = re.compile(r"`([A-Z]{2,}-\d{3})`")
_FRONTMATTER = re.compile(r"\A---\s*\n(.*?)\n---\s*\n", re.DOTALL)
_HEADING = re.compile(r"^##\s+(.+?)\s*$", re.MULTILINE)
_FENCED_BLOCK = re.compile(r"```[^\n]*\n(.*?)```", re.DOTALL)


class StandardsError(RuntimeError):
    """Raised when the pinned standards checkout cannot be resolved or parsed."""


@dataclass(frozen=True)
class RuleRecord:
    """One normative rule from ``rule_map.toml``."""

    rule_id: str
    source: str
    section: str
    behavior: str
    scenarios: tuple[str, ...]


@dataclass(frozen=True)
class TriggerCase:
    """One activation case of a trigger set."""

    prompt: str
    should_trigger: bool
    note: str


@dataclass(frozen=True)
class Scenario:
    """Parsed standards-side scenario contract."""

    scenario_id: str
    title: str
    kind: str
    path: Path
    referenced_ids: tuple[str, ...]
    enabled_features: tuple[str, ...]
    fixture_text: str
    prompt: str
    invariants: tuple[str, ...]
    forbidden: tuple[str, ...]
    trigger_cases: tuple[TriggerCase, ...]


@contextmanager
def resolve_standards_checkout(config: EvalConfig) -> Iterator[Path]:
    """Materialize the pinned standards revision as a temporary read-only worktree."""
    repo = config.standards_repo
    run_git(repo, "rev-parse", "--verify", f"{config.standards_revision}^{{commit}}")
    with tempfile.TemporaryDirectory(prefix="ai-standards-evals-") as tmp:
        worktree = Path(tmp) / "standards"
        run_git(repo, "worktree", "add", "--detach", str(worktree), config.standards_revision)
        try:
            yield worktree
        finally:
            run_git(repo, "worktree", "remove", "--force", str(worktree))


def load_rule_map(worktree: Path) -> dict[str, RuleRecord]:
    """Parse ``rule_map.toml`` from the pinned standards revision."""
    rule_map_path = worktree / "rule_map.toml"
    data = tomllib.loads(rule_map_path.read_text(encoding="utf-8"))
    rules = cast("dict[str, dict[str, object]]", data.get("rules", {}))
    records: dict[str, RuleRecord] = {}
    for rule_id, entry in rules.items():
        source = entry.get("source")
        if not isinstance(source, str):
            source = f"{cast('str', entry['fragment'])}.md"
        records[rule_id] = RuleRecord(
            rule_id=rule_id,
            source=source,
            section=cast("str", entry["section"]),
            behavior=cast("str", entry["behavior"]),
            scenarios=tuple(cast("list[str]", entry.get("scenarios", []))),
        )
    return records


def verifies_rules(scenario: Scenario, rule_map: dict[str, RuleRecord]) -> tuple[str, ...]:
    """Rule IDs referenced by the scenario intro that exist in the rule map."""
    return tuple(rule_id for rule_id in scenario.referenced_ids if rule_id in rule_map)


def index_scenarios(worktree: Path) -> dict[str, Scenario]:
    """Index every canonical (non-localized) scenario contract of the revision."""
    scenarios_dir = worktree / "docs" / "scenarios"
    if not scenarios_dir.is_dir():
        msg = f"scenarios directory is missing in the pinned revision: {scenarios_dir}"
        raise StandardsError(msg)
    index: dict[str, Scenario] = {}
    for path in sorted(scenarios_dir.glob("*.md")):
        if path.name.endswith(".ru.md"):
            continue
        if _SCENARIO_FILE.match(path.name) is None:
            continue
        scenario = parse_scenario(path)
        index[scenario.scenario_id] = scenario
    return index


def parse_scenario(path: Path) -> Scenario:
    """Parse one scenario contract file into a :class:`Scenario`."""
    match = _SCENARIO_FILE.match(path.name)
    if match is None:
        msg = f"not a canonical scenario file name: {path.name}"
        raise StandardsError(msg)
    scenario_id = match.group(1)
    text = path.read_text(encoding="utf-8")
    _, body = _strip_frontmatter(text)
    sections = _sections(body)
    features = tuple(
        found.group(1)
        for line in _dash_items(sections.get("Enabled Features", ""))
        if (found := re.search(r"`([^`]+)`", line))
    )
    is_trigger_set = "Positive Cases" in sections
    if is_trigger_set:
        cases = (
            _parse_trigger_cases(sections.get("Positive Cases", ""))
            + _parse_trigger_cases(sections.get("Negative Cases", ""))
            + _parse_trigger_cases(sections.get("Boundary Cases", ""))
        )
        return Scenario(
            scenario_id=scenario_id,
            title=_title(text),
            kind=KIND_TRIGGER_SET,
            path=path,
            referenced_ids=_referenced_ids(body),
            enabled_features=features,
            fixture_text="",
            prompt="",
            invariants=(),
            forbidden=(),
            trigger_cases=cases,
        )
    return Scenario(
        scenario_id=scenario_id,
        title=_title(text),
        kind=KIND_BEHAVIOR,
        path=path,
        referenced_ids=_referenced_ids(body),
        enabled_features=features,
        fixture_text=sections.get("Fixture", "").strip(),
        prompt=_fenced_block(sections.get("Prompt", "")),
        invariants=_numbered_items(sections.get("Expected Observable Invariants", "")),
        forbidden=_dash_items(sections.get("Forbidden Outcomes", "")),
        trigger_cases=(),
    )


def _strip_frontmatter(text: str) -> tuple[str, str]:
    match = _FRONTMATTER.match(text)
    if match is None:
        return "", text
    return match.group(1), text[match.end() :]


def _title(text: str) -> str:
    frontmatter, _ = _strip_frontmatter(text)
    for line in frontmatter.splitlines():
        if line.startswith("title:"):
            return line.split(":", 1)[1].strip().strip("'\"")
    return ""


def _sections(body: str) -> dict[str, str]:
    matches = list(_HEADING.finditer(body))
    sections: dict[str, str] = {}
    for index, match in enumerate(matches):
        start = match.end()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(body)
        sections[match.group(1)] = body[start:end]
    return sections


def _referenced_ids(body: str) -> tuple[str, ...]:
    intro = body
    match = _HEADING.search(body)
    if match is not None:
        intro = body[: match.start()]
    return _backticked_ids(intro)


def _backticked_ids(text: str) -> tuple[str, ...]:
    seen: list[str] = []
    for candidate in _ID_REFERENCE.findall(text):
        if candidate not in seen:
            seen.append(candidate)
    return tuple(seen)


def _fenced_block(text: str) -> str:
    match = _FENCED_BLOCK.search(text)
    return match.group(1).strip() if match else ""


def _numbered_items(text: str) -> tuple[str, ...]:
    items = []
    for line in text.splitlines():
        found = re.match(r"^\d+\.\s+(.*)$", line.strip())
        if found:
            items.append(found.group(1).strip())
    return tuple(items)


def _dash_items(text: str) -> tuple[str, ...]:
    return tuple(
        line.strip()[2:].strip() for line in text.splitlines() if line.strip().startswith("- ")
    )


def _table_rows(text: str) -> list[tuple[str, ...]]:
    rows: list[tuple[str, ...]] = []
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped.startswith("|"):
            continue
        if set(stripped) <= {"|", "-", " ", ":"}:
            continue
        rows.append(tuple(cell.strip() for cell in stripped.strip("|").split("|")))
    return rows


def _parse_trigger_cases(section_text: str) -> tuple[TriggerCase, ...]:
    cases: list[TriggerCase] = []
    for row in _table_rows(section_text):
        if len(row) < 2:
            continue
        prompt, expected = row[0], row[1]
        if not expected.strip().lower().startswith(("true", "false")):
            continue
        cases.append(
            TriggerCase(
                prompt=prompt,
                should_trigger=expected.strip().lower().startswith("true"),
                note=expected.partition("—")[2].strip(),
            )
        )
    return tuple(cases)
