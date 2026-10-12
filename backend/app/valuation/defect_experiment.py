from copy import deepcopy

from backend.app.valuation.impact_analyzer import (
    assess_materiality,
    compare_portfolios,
    rank_defect_impacts,
)


def run_defect_experiment(
    clean_policies: list[dict],
    defects: list[dict],
    claim_probability: float,
    materiality_threshold_percent: float = 5.0,
) -> dict:
    """
    Measure the isolated simulated impact of each supplied defect.

    Each defect must contain:
    - defect_id: a unique identifier
    - policy_id: the policy to modify
    - field: the field to modify
    - altered_value: the value to substitute

    The clean portfolio is never modified.
    """
    if not 0 <= claim_probability <= 1:
        raise ValueError("Claim probability must be between 0 and 1.")

    baseline_cost = compare_portfolios(
        clean_policies,
        clean_policies,
        claim_probability,
    )["clean_expected_cost"]

    if baseline_cost <= 0 and defects:
        raise ValueError(
            "Baseline expected cost must be greater than zero " "to assess materiality."
        )

    seen_defect_ids = set()
    seen_targets = set()
    results = []

    for defect in defects:
        required_fields = {
            "defect_id",
            "policy_id",
            "field",
            "altered_value",
        }

        if not required_fields.issubset(defect):
            raise ValueError(
                "Each defect must contain defect_id, policy_id, "
                "field, and altered_value."
            )

        defect_id = defect["defect_id"]

        if defect_id in seen_defect_ids:
            raise ValueError(f"Duplicate defect_id: {defect_id}")

        seen_defect_ids.add(defect_id)

        if defect["field"] != "sum_assured":
            raise ValueError(
                "This experiment currently supports only sum_assured " "defects."
            )

        target = (defect["policy_id"], defect["field"])

        if target in seen_targets:
            raise ValueError(
                "Only one defect per policy field is supported "
                "in an isolated experiment."
            )

        seen_targets.add(target)

        altered_policies = deepcopy(clean_policies)

        matching_policies = [
            policy
            for policy in altered_policies
            if policy.get("policy_id") == defect["policy_id"]
        ]

        if len(matching_policies) != 1:
            raise ValueError(
                f"Expected exactly one policy with ID " f"{defect['policy_id']!r}."
            )

        original_value = matching_policies[0]["sum_assured"]

        if "original_value" in defect and float(defect["original_value"]) != float(
            original_value
        ):
            raise ValueError(
                f"Scenario {defect_id!r} has an original_value "
                f"that does not match policy {defect['policy_id']!r}."
            )

        matching_policies[0]["sum_assured"] = defect["altered_value"]

        comparison = compare_portfolios(
            clean_policies,
            altered_policies,
            claim_probability,
        )

        impact = comparison["impact"]

        materiality = assess_materiality(
            impact,
            baseline_cost,
            materiality_threshold_percent,
        )

        results.append(
            {
                "defect_id": defect_id,
                "policy_id": defect["policy_id"],
                "field": defect["field"],
                "original_value": original_value,
                "altered_value": defect["altered_value"],
                "impact": impact,
                "absolute_impact": abs(impact),
                "impact_percent": materiality["impact_percent"],
                "is_material": materiality["is_material"],
            }
        )

    ranked_results = rank_defect_impacts(results)

    # Apply all defects together to measure their combined impact.
    combined_policies = deepcopy(clean_policies)

    for defect in defects:
        matching_policy = next(
            policy
            for policy in combined_policies
            if policy.get("policy_id") == defect["policy_id"]
        )
        matching_policy["sum_assured"] = defect["altered_value"]

    combined_comparison = compare_portfolios(
        clean_policies,
        combined_policies,
        claim_probability,
    )

    combined_impact = combined_comparison["impact"]
    sum_isolated_impacts = sum(result["impact"] for result in results)

    interaction_residual = combined_impact - sum_isolated_impacts

    return {
        "baseline_expected_cost": baseline_cost,
        "claim_probability": claim_probability,
        "materiality_threshold_percent": materiality_threshold_percent,
        "defect_count": len(ranked_results),
        "material_defect_count": sum(
            result["is_material"] for result in ranked_results
        ),
        "ranked_defects": ranked_results,
        "combined_impact": combined_impact,
        "sum_isolated_impacts": sum_isolated_impacts,
        "interaction_residual": interaction_residual,
        "valuation_basis": (
            "Simplified educational simulation; not a production "
            "actuarial valuation."
        ),
    }

    return {
        "baseline_expected_cost": baseline_cost,
        "claim_probability": claim_probability,
        "materiality_threshold_percent": materiality_threshold_percent,
        "defect_count": len(ranked_results),
        "material_defect_count": sum(
            result["is_material"] for result in ranked_results
        ),
        "ranked_defects": ranked_results,
        "valuation_basis": (
            "Simplified educational simulation; not a production "
            "actuarial valuation."
        ),
    }
