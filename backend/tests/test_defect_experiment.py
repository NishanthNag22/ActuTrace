import pytest

from backend.app.valuation.defect_experiment import (
    run_defect_experiment,
)


@pytest.fixture
def clean_policies():
    return [
        {"policy_id": "P1001", "sum_assured": 500000},
        {"policy_id": "P1002", "sum_assured": 300000},
    ]


def test_experiment_measures_and_ranks_defects(clean_policies):
    defects = [
        {
            "defect_id": "D1",
            "policy_id": "P1001",
            "field": "sum_assured",
            "altered_value": 400000,
        },
        {
            "defect_id": "D2",
            "policy_id": "P1002",
            "field": "sum_assured",
            "altered_value": 100000,
        },
    ]

    result = run_defect_experiment(
        clean_policies,
        defects,
        claim_probability=0.02,
        materiality_threshold_percent=5,
    )

    assert result["baseline_expected_cost"] == 16000
    assert result["defect_count"] == 2
    assert result["ranked_defects"][0]["defect_id"] == "D2"
    assert result["ranked_defects"][0]["impact"] == -4000
    assert result["ranked_defects"][1]["impact"] == -2000


def test_experiment_does_not_modify_clean_portfolio(clean_policies):
    original = [policy.copy() for policy in clean_policies]

    run_defect_experiment(
        clean_policies,
        [
            {
                "defect_id": "D1",
                "policy_id": "P1001",
                "field": "sum_assured",
                "altered_value": 400000,
            }
        ],
        claim_probability=0.02,
    )

    assert clean_policies == original


def test_experiment_rejects_unknown_policy(clean_policies):
    defects = [
        {
            "defect_id": "D1",
            "policy_id": "UNKNOWN",
            "field": "sum_assured",
            "altered_value": 100000,
        }
    ]

    with pytest.raises(ValueError, match="Expected exactly one policy"):
        run_defect_experiment(clean_policies, defects, 0.02)


def test_experiment_rejects_unsupported_field(clean_policies):
    defects = [
        {
            "defect_id": "D1",
            "policy_id": "P1001",
            "field": "annual_premium",
            "altered_value": 1000,
        }
    ]

    with pytest.raises(ValueError, match="currently supports only"):
        run_defect_experiment(clean_policies, defects, 0.02)


def test_experiment_rejects_duplicate_defect_ids(clean_policies):
    defect = {
        "defect_id": "D1",
        "policy_id": "P1001",
        "field": "sum_assured",
        "altered_value": 400000,
    }

    with pytest.raises(ValueError, match="Duplicate defect_id"):
        run_defect_experiment(
            clean_policies,
            [defect, defect.copy()],
            0.02,
        )


def test_experiment_rejects_zero_baseline():
    with pytest.raises(ValueError, match="greater than zero"):
        run_defect_experiment(
            [{"policy_id": "P1001", "sum_assured": 0}],
            [
                {
                    "defect_id": "D1",
                    "policy_id": "P1001",
                    "field": "sum_assured",
                    "altered_value": 100000,
                }
            ],
            0.02,
        )


def test_combined_impact_matches_isolated_impacts_in_linear_model(
    clean_policies,
):
    defects = [
        {
            "defect_id": "D1",
            "policy_id": "P1001",
            "field": "sum_assured",
            "altered_value": 400000,
        },
        {
            "defect_id": "D2",
            "policy_id": "P1002",
            "field": "sum_assured",
            "altered_value": 100000,
        },
    ]

    result = run_defect_experiment(
        clean_policies,
        defects,
        claim_probability=0.02,
    )

    assert result["combined_impact"] == -6000.0
    assert result["sum_isolated_impacts"] == -6000.0
    assert result["interaction_residual"] == 0.0


def test_no_defects_produce_zero_combined_impact(clean_policies):
    result = run_defect_experiment(
        clean_policies,
        [],
        claim_probability=0.02,
    )

    assert result["combined_impact"] == 0.0
    assert result["sum_isolated_impacts"] == 0.0
    assert result["interaction_residual"] == 0.0
