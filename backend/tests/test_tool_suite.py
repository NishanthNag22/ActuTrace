import pytest
from backend.app.valuation.tool_suite import compare_model_outputs, project_liability, simulate_pricing


def test_model_monitor_flags_material_change():
    result = compare_model_outputs({"reserve": 100.0, "profit": 50.0}, {"reserve": 110.0, "profit": 49.0}, 5.0)
    assert result["flagged_metric_count"] == 1
    assert result["results"][0]["metric"] == "reserve"
    assert result["results"][0]["flagged"] is True


def test_model_monitor_rejects_mismatched_metrics():
    with pytest.raises(ValueError):
        compare_model_outputs({"reserve": 10}, {"profit": 11})


def test_pricing_scenario_calculates_illustrative_amounts():
    result = simulate_pricing(100_000, 0.02, 10, 5)
    assert result["expected_claim_cost"] == 2000
    assert result["illustrative_premium"] == 2300


def test_liability_projection_compounds_growth():
    result = project_liability(1000, 10, 2)
    assert result["schedule"][0]["projected_amount"] == pytest.approx(1100)
    assert result["ending_amount"] == pytest.approx(1210)


def test_liability_projection_rejects_invalid_horizon():
    with pytest.raises(ValueError):
        project_liability(1000, 2, 0)
