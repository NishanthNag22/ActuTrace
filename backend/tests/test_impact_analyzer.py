
import pytest

from backend.app.valuation.impact_analyzer import compare_portfolios


def test_portfolio_comparison_calculates_impact():
    clean = [
        {"sum_assured": 500000},
        {"sum_assured": 300000},
    ]
    altered = [
        {"sum_assured": 500000},
        {"sum_assured": 200000},
    ]

    result = compare_portfolios(clean, altered, 0.02)

    assert result["clean_expected_cost"] == 16000.0
    assert result["altered_expected_cost"] == 14000.0
    assert result["impact"] == -2000.0
    assert result["absolute_impact"] == 2000.0


def test_identical_portfolios_have_zero_impact():
    policies = [{"sum_assured": 500000}]

    result = compare_portfolios(policies, policies, 0.02)

    assert result["impact"] == 0.0
    assert result["absolute_impact"] == 0.0


def test_invalid_claim_probability_is_rejected():
    policies = [{"sum_assured": 500000}]

    with pytest.raises(ValueError, match="between 0 and 1"):
        compare_portfolios(policies, policies, 1.5)


from backend.app.valuation.impact_analyzer import (
    assess_materiality,
    rank_defect_impacts,
)


def test_defects_are_ranked_by_absolute_impact():
    results = [
        {"defect_id": "A", "impact": 100},
        {"defect_id": "B", "impact": -500},
        {"defect_id": "C", "impact": 250},
    ]

    ranked = rank_defect_impacts(results)

    assert [item["defect_id"] for item in ranked] == ["B", "C", "A"]
    assert ranked[0]["absolute_impact"] == 500


def test_ranking_preserves_signed_impact():
    results = [{"defect_id": "A", "impact": -200}]

    ranked = rank_defect_impacts(results)

    assert ranked[0]["impact"] == -200
    assert ranked[0]["absolute_impact"] == 200


def test_ranking_rejects_missing_fields():
    with pytest.raises(ValueError, match="must contain defect_id and impact"):
        rank_defect_impacts([{"impact": 100}])


def test_materiality_threshold_is_applied():
    result = assess_materiality(
        impact=6000,
        baseline_value=100000,
        threshold_percent=5,
    )

    assert result["impact_percent"] == 6
    assert result["is_material"] is True


def test_impact_below_materiality_threshold():
    result = assess_materiality(
        impact=2000,
        baseline_value=100000,
        threshold_percent=5,
    )

    assert result["impact_percent"] == 2
    assert result["is_material"] is False


def test_materiality_requires_positive_baseline():
    with pytest.raises(ValueError, match="greater than zero"):
        assess_materiality(100, 0, 5)
