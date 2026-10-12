
import csv
import json

import pytest

from backend.app.analysis_workflow import run_actutrace_analysis


@pytest.fixture
def analysis_files(tmp_path):
    policy_csv = tmp_path / "policies.csv"
    policy_csv.write_text(
        "policy_id,date_of_birth,policy_start_date,"
        "policy_term_years,sum_assured,annual_premium,policy_status\n"
        "P1001,1985-04-12,2020-01-01,20,500000,12000,active\n"
        "P1002,,2021-06-15,15,300000,8500,active\n",
        encoding="utf-8",
    )

    clean_csv = tmp_path / "clean.csv"
    clean_csv.write_text(
        "policy_id,sum_assured\n"
        "P1001,500000\n"
        "P1002,300000\n",
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
        },
        {
            "defect_id": "D002",
            "policy_id": "P1002",
            "field": "sum_assured",
            "original_value": 300000,
            "altered_value": 100000,
            "description": "Controlled reduction",
        },
    ]

    scenario_json = tmp_path / "scenarios.json"
    scenario_json.write_text(
        json.dumps(scenarios),
        encoding="utf-8",
    )

    return policy_csv, clean_csv, scenario_json, tmp_path / "reports"


def test_workflow_combines_validation_and_valuation(analysis_files):
    policy_csv, clean_csv, scenarios, reports = analysis_files

    result = run_actutrace_analysis(
        policy_csv,
        clean_csv,
        scenarios,
        reports,
    )

    assert result["application"] == "ActuTrace"
    assert result["validation"]["finding_count"] >= 1
    assert result["valuation"]["defect_count"] == 2
    assert result["valuation"]["baseline_expected_cost"] == 16000
    assert result["valuation"]["combined_impact"] == -6000
    assert result["valuation"]["interaction_residual"] == 0


def test_workflow_creates_all_three_reports(analysis_files):
    policy_csv, clean_csv, scenarios, reports = analysis_files

    run_actutrace_analysis(
        policy_csv,
        clean_csv,
        scenarios,
        reports,
    )

    assert (reports / "validation_findings.csv").is_file()
    assert (reports / "valuation_impacts.csv").is_file()
    assert (reports / "analysis_summary.json").is_file()


def test_valuation_report_is_ranked(analysis_files):
    policy_csv, clean_csv, scenarios, reports = analysis_files

    run_actutrace_analysis(
        policy_csv,
        clean_csv,
        scenarios,
        reports,
    )

    with (reports / "valuation_impacts.csv").open(
        "r",
        newline="",
        encoding="utf-8-sig",
    ) as csv_file:
        rows = list(csv.DictReader(csv_file))

    assert rows[0]["defect_id"] == "D002"
    assert rows[1]["defect_id"] == "D001"
    assert rows[0]["rank"] == "1"


def test_workflow_rejects_mismatched_scenario_baseline(analysis_files):
    policy_csv, clean_csv, scenarios, reports = analysis_files

    scenario_data = json.loads(scenarios.read_text(encoding="utf-8"))
    scenario_data[0]["original_value"] = 450000
    scenarios.write_text(json.dumps(scenario_data), encoding="utf-8")

    with pytest.raises(ValueError, match="original_value"):
        run_actutrace_analysis(
            policy_csv,
            clean_csv,
            scenarios,
            reports,
        )


def test_workflow_rejects_missing_policy_columns(analysis_files):
    _, clean_csv, scenarios, reports = analysis_files
    incomplete_csv = reports.parent / "incomplete.csv"
    incomplete_csv.write_text(
        "policy_id,sum_assured\nP1001,500000\n",
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="missing required columns"):
        run_actutrace_analysis(
            incomplete_csv,
            clean_csv,
            scenarios,
            reports,
        )
