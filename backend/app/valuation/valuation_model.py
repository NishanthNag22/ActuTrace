
def estimate_simple_claim_amount(sum_assured: float) -> float:
    """Estimate a simplified claim amount for an educational simulation."""
    if sum_assured < 0:
        raise ValueError("Sum assured cannot be negative.")

    return float(sum_assured)


def estimate_expected_claim_cost(
    sum_assured: float,
    claim_probability: float,
) -> float:
    """
    Estimate expected claim cost using an assumed claim probability.

    This is an educational simulation, not a production actuarial model.
    """
    if sum_assured < 0:
        raise ValueError("Sum assured cannot be negative.")

    if not 0 <= claim_probability <= 1:
        raise ValueError("Claim probability must be between 0 and 1.")

    return float(sum_assured) * claim_probability


def estimate_portfolio_expected_cost(
    policies: list[dict],
    claim_probability: float,
) -> float:
    """
    Calculate the expected claim cost across a portfolio of policies.

    Each policy must contain a numeric, non-negative sum_assured.
    """
    if not 0 <= claim_probability <= 1:
        raise ValueError("Claim probability must be between 0 and 1.")

    total_cost = 0.0

    for policy in policies:
        if "sum_assured" not in policy:
            raise ValueError("Every policy must contain sum_assured.")

        total_cost += estimate_expected_claim_cost(
            float(policy["sum_assured"]),
            claim_probability,
        )

    return total_cost
