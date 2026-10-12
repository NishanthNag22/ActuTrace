
import json

import pytest

from backend.app.valuation.experiment_runner import (
    load_clean_policies,
    run_scenario_file,
)


def test_load_clean_policies_rejects_duplicate_ids(tmp_path):
    csv_path = tmp_path / "clean.csv"
    csv_path.write_text(
        "policy_id,sum_assured\nP1001,500000\nP1001,300000\n",
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="duplicate policy ID"):
        load_clean_policies(csv_path)


def test_scenario_file_runs_against_clean_baseline(tmp_path):
    clean_csv = tmp_path / "clean.csv"
    clean_csv.write_text(
        "policy_id,sum_assured\nP1001,500000\nP1002,300000\n",
        encoding="utf-8",
    )

    scenarios = [
        {
            "defect_id": "D001",
            "policy_id": "P1001",
            "field": "sum_assured",
            "original_value": 500000,
            "altered_value": 400000,
            "description": "Controlled reduction",
        }
    ]

    scenario_json = tmp_path / "scenarios.json"
    scenario_json.write_text(json.dumps(scenarios), encoding="utf-8")

    result = run_scenario_file(clean_csv, scenario_json)

    assert result["baseline_expected_cost"] == 16000
    assert result["defect_count"] == 1
    assert result["ranked_defects"][0]["impact"] == -2000


def test_scenario_rejects_mismatched_original_value(tmp_path):
    clean_csv = tmp_path / "clean.csv"
    clean_csv.write_text(
        "policy_id,sum_assured\nP1001,500000\n",
        encoding="utf-8",
    )

    scenarios = [
        {
            "defect_id": "D001",
            "policy_id": "P1001",
            "field": "sum_assured",
            "original_value": 450000,
            "altered_value": 400000,
            "description": "Incorrect baseline",
        }
    ]

    scenario_json = tmp_path / "scenarios.json"
    scenario_json.write_text(json.dumps(scenarios), encoding="utf-8")

    with pytest.raises(ValueError, match="original_value"):
        run_scenario_file(clean_csv, scenario_json)
