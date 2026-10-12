
from backend.app.valuation.valuation_model import (
    estimate_portfolio_expected_cost,
)


def compare_portfolios(
    clean_policies: list[dict],
    altered_policies: list[dict],
    claim_probability: float,
) -> dict:
    """
    Compare clean and altered portfolios.

    Impact is altered cost minus clean cost. This is a simulated
    difference, not a production actuarial valuation.
    """
    clean_cost = estimate_portfolio_expected_cost(
        clean_policies,
        claim_probability,
    )
    altered_cost = estimate_portfolio_expected_cost(
        altered_policies,
        claim_probability,
    )

    impact = altered_cost - clean_cost

    return {
        "clean_expected_cost": clean_cost,
        "altered_expected_cost": altered_cost,
        "impact": impact,
        "absolute_impact": abs(impact),
    }


def rank_defect_impacts(defect_results: list[dict]) -> list[dict]:
    """
    Rank defect results by absolute simulated financial impact.

    Each result must include:
    - defect_id
    - impact
    """
    for result in defect_results:
        if "defect_id" not in result or "impact" not in result:
            raise ValueError("Each result must contain defect_id and impact.")

        if not isinstance(result["impact"], (int, float)):
            raise ValueError("Each impact must be numeric.")

    return sorted(
        [
            {**result, "absolute_impact": abs(result["impact"])}
            for result in defect_results
        ],
        key=lambda result: result["absolute_impact"],
        reverse=True,
    )


def assess_materiality(
    impact: float,
    baseline_value: float,
    threshold_percent: float,
) -> dict:
    """
    Assess whether an absolute impact meets a percentage threshold.

    The baseline must be positive. The threshold is a percentage,
    such as 5 for five percent.
    """
    if baseline_value <= 0:
        raise ValueError("Baseline value must be greater than zero.")

    if threshold_percent < 0:
        raise ValueError("Threshold percentage cannot be negative.")

    impact_percent = abs(impact) / baseline_value * 100

    return {
        "impact": impact,
        "absolute_impact": abs(impact),
        "impact_percent": impact_percent,
        "threshold_percent": threshold_percent,
        "is_material": impact_percent >= threshold_percent,
    }
