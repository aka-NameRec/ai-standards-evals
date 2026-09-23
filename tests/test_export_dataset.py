"""Tests for the dataset snapshot export."""

from __future__ import annotations

from scripts.export_dataset import dataset_records


def test_dataset_records_flag_fixture_builders() -> None:
    scenarios = {
        "CR-002": {
            "title": "Scenario CR-002: sample",
            "kind": "behavior",
            "enabled_features": ["code-review"],
            "prompt": "code review",
        },
        "SK-099": {
            "title": "Scenario SK-099: no builder",
            "kind": "behavior",
            "enabled_features": ["skill-engineering"],
            "prompt": "create a skill",
        },
    }

    records = dataset_records(scenarios, {"CR-002"})

    by_id = {record["scenario_id"]: record for record in records}
    assert by_id["CR-002"]["fixture_builder"] is True
    assert by_id["SK-099"]["fixture_builder"] is False
    assert by_id["CR-002"]["prompt"] == "code review"
    assert records[0]["scenario_id"] == "CR-002"
