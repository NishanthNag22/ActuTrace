
import json

import pytest

from backend.app.valuation.scenario_loader import (
    load_defect_scenarios,
)


def test_loads_valid_scenarios(tmp_path):
    scenarios = [
        {
            "defect_id": "D001",
            "policy_id": "P1001",
            "field": "sum_assured",
            "original_value": 500000,
            "altered_value": 400000,
            "description": "Controlled test defect",
        }
    ]

    scenario_file = tmp_path / "scenarios.json"
    scenario_file.write_text(
        json.dumps(scenarios),
        encoding="utf-8",
    )

    result = load_defect_scenarios(scenario_file)

    assert result == scenarios


def test_rejects_non_list_json(tmp_path):
    scenario_file = tmp_path / "scenarios.json"
    scenario_file.write_text(
        '{"defect_id": "D001"}',
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="JSON list"):
        load_defect_scenarios(scenario_file)


def test_rejects_missing_fields(tmp_path):
    scenario_file = tmp_path / "scenarios.json"
    scenario_file.write_text(
        '[{"defect_id": "D001"}]',
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="missing fields"):
        load_defect_scenarios(scenario_file)


def test_rejects_duplicate_ids(tmp_path):
    scenario = {
        "defect_id": "D001",
        "policy_id": "P1001",
        "field": "sum_assured",
        "original_value": 500000,
        "altered_value": 400000,
        "description": "Controlled test defect",
    }

    scenario_file = tmp_path / "scenarios.json"
    scenario_file.write_text(
        json.dumps([scenario, scenario]),
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="Duplicate defect_id"):
        load_defect_scenarios(scenario_file)


def test_rejects_negative_original_value(tmp_path):
    scenario = {
        "defect_id": "D001",
        "policy_id": "P1001",
        "field": "sum_assured",
        "original_value": -500000,
        "altered_value": 400000,
        "description": "Invalid original value",
    }

    scenario_file = tmp_path / "scenarios.json"
    scenario_file.write_text(
        json.dumps([scenario]),
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="cannot be negative"):
        load_defect_scenarios(scenario_file)
