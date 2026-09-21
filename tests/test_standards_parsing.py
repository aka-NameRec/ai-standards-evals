"""Tests for standards-side scenario contract parsing."""

from __future__ import annotations

from pathlib import Path

from scripts.standards import (
    KIND_BEHAVIOR,
    KIND_TRIGGER_SET,
    load_rule_map,
    parse_scenario,
    verifies_rules,
)

BEHAVIOR_SAMPLE = """---
title: 'Scenario TST-001: sample behavior'
permalink: ai-standards/scenarios/TST-001-sample
---

# Scenario TST-001: sample behavior

Behavioral scenario for the code-review workflow. Verifies rules `RVW-006`
and `RVW-010`. Status: draft.

## Fixture

Pre-state: sample pre-state.

Diff under review: sample diff.

## Enabled Features

- `code-review`

## Prompt

```text
code review
```

## Expected Observable Invariants

1. First invariant (`RVW-006`).
2. Second invariant.

## Forbidden Outcomes

- Forbidden one.
- Forbidden two.

## Observations

- [fact] Sample observation.

## Relations

- implements [[DECISION: sample]]
"""

TRIGGER_SAMPLE = """---
title: 'Activation trigger set TST-002: sample skill'
permalink: ai-standards/scenarios/TST-002-sample
---

# Activation trigger set TST-002: sample skill

Activation trigger set for the `sample` skill. Verifies rule `RVW-029` and `SE-008`.

## Enabled Features

- `code-review`

## Positive Cases

| prompt | expected should_trigger |
|---|---|
| standard code review | true |
| run the standard review | true — explicitly named |

## Negative Cases

| prompt | expected should_trigger |
|---|---|
| code review | false — the bare default workflow, not the skill |
| write tests | false |

## Boundary Cases

| prompt | expected should_trigger |
|---|---|
| code review по стандарту проекта | true — the standard is named |

## Observations

- [fact] Sample.

## Relations

- implements [[DECISION: sample]]
"""

RULE_MAP_SAMPLE = """
[rules.RVW-006]
fragment = "process/code-review"
section = "What To Check"
behavior = "reuse and duplication"
scenarios = ["TST-001"]

[rules.RVW-029]
fragment = "process/code-review"
section = "Relationship To Review Lenses"
behavior = "activation phrases"
scenarios = ["TST-002"]
"""


def _write(path: Path, content: str) -> Path:
    path.write_text(content, encoding="utf-8")
    return path


def test_parse_behavior_scenario(tmp_path: Path) -> None:
    scenario = parse_scenario(_write(tmp_path / "TST-001-sample.md", BEHAVIOR_SAMPLE))

    assert scenario.scenario_id == "TST-001"
    assert scenario.kind == KIND_BEHAVIOR
    assert scenario.title == "Scenario TST-001: sample behavior"
    assert scenario.referenced_ids == ("RVW-006", "RVW-010")
    assert scenario.enabled_features == ("code-review",)
    assert scenario.prompt == "code review"
    assert scenario.fixture_text.startswith("Pre-state:")
    assert scenario.invariants[0].startswith("First invariant")
    assert scenario.forbidden == ("Forbidden one.", "Forbidden two.")


def test_parse_trigger_set_scenario(tmp_path: Path) -> None:
    scenario = parse_scenario(_write(tmp_path / "TST-002-sample.md", TRIGGER_SAMPLE))

    assert scenario.kind == KIND_TRIGGER_SET
    assert scenario.prompt == ""
    assert [case.should_trigger for case in scenario.trigger_cases] == [
        True,
        True,
        False,
        False,
        True,
    ]
    assert scenario.trigger_cases[1].note == "explicitly named"
    assert (
        scenario.trigger_cases[2].note == "the bare default workflow, not the skill"
    )
    assert scenario.trigger_cases[4].prompt == "code review по стандарту проекта"


def test_verifies_rules_intersects_rule_map(tmp_path: Path) -> None:
    scenario = parse_scenario(_write(tmp_path / "TST-001-sample.md", BEHAVIOR_SAMPLE))
    worktree = tmp_path / "wt"
    worktree.mkdir()
    _write(worktree / "rule_map.toml", RULE_MAP_SAMPLE)

    assert verifies_rules(scenario, load_rule_map(worktree)) == ("RVW-006",)
