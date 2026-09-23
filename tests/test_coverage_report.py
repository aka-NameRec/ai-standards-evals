"""Tests for the rule-to-scenario coverage aggregation."""

from __future__ import annotations

from scripts.coverage_report import build_coverage
from scripts.standards import RuleRecord


def _rule(rule_id: str, scenarios: tuple[str, ...]) -> RuleRecord:
    return RuleRecord(
        rule_id=rule_id,
        source="fragments/process/x.md",
        section="Section",
        behavior="behavior statement",
        scenarios=scenarios,
    )


def test_build_coverage_aggregates_bound_and_unbound_rules() -> None:
    rules = {
        "RVW-006": _rule("RVW-006", ("CR-001", "CR-005")),
        "RVW-099": _rule("RVW-099", ()),
    }

    report = build_coverage(
        rules,
        ["CR-001", "CR-005"],
        {"CR-001": "behavior", "CR-005": "behavior"},
    )

    assert report["rules_total"] == 2
    assert report["rules_with_scenarios"] == 1
    assert report["rules_without_scenarios"] == ["RVW-099"]
    assert report["coverage"] == {"RVW-006": ["CR-001", "CR-005"]}
    assert report["scenarios_by_kind"] == {"behavior": 2}


def test_build_coverage_handles_empty_inputs() -> None:
    report = build_coverage({}, [], {})

    assert report["rules_total"] == 0
    assert report["scenarios_total"] == 0
    assert report["scenarios_by_kind"] == {}
