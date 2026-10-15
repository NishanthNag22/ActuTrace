
import pytest

from backend.app.valuation.priority_comparator import (
    compare_priority_methods,
)


def test_financial_impact_ranking_differs_from_count_ranking():
    records = [
        {"defect_type": "Missing dates", "impact": -100},
        {"defect_type": "Missing dates", "impact": -100},
        {"defect_type": "Missing dates", "impact": -100},
        {"defect_type": "Incorrect sum assured", "impact": -5000},
    ]

    result = compare_priority_methods(records)

    by_type = {
        item["defect_type"]: item
        for item in result["results"]
    }

    assert by_type["Missing dates"]["count_rank"] == 1
    assert by_type["Incorrect sum assured"]["count_rank"] == 2

    assert by_type["Incorrect sum assured"]["impact_rank"] == 1
    assert by_type["Missing dates"]["impact_rank"] == 2

    assert result["ranking_differs"] is True
    assert result["spearman_rank_correlation"] == -1.0


def test_equal_rankings_have_perfect_positive_correlation():
    records = [
        {"defect_type": "A", "impact": -500},
        {"defect_type": "A", "impact": -400},
        {"defect_type": "B", "impact": -100},
    ]

    result = compare_priority_methods(records)

    assert result["ranking_differs"] is False
    assert result["spearman_rank_correlation"] == 1.0


def test_tied_counts_use_average_ranks():
    records = [
        {"defect_type": "A", "impact": -100},
        {"defect_type": "B", "impact": -500},
    ]

    result = compare_priority_methods(records)

    by_type = {
        item["defect_type"]: item
        for item in result["results"]
    }

    assert by_type["A"]["count_rank"] == 1.5
    assert by_type["B"]["count_rank"] == 1.5
    assert result["ranking_differs"] is True


def test_empty_records_are_rejected():
    with pytest.raises(ValueError, match="At least one"):
        compare_priority_methods([])


def test_missing_record_fields_are_rejected():
    with pytest.raises(ValueError, match="defect_type and impact"):
        compare_priority_methods(
            [{"defect_type": "Missing dates"}]
        )


def test_invalid_impact_is_rejected():
    with pytest.raises(ValueError, match="finite number"):
        compare_priority_methods(
            [{"defect_type": "Missing dates", "impact": float("nan")}]
        )
