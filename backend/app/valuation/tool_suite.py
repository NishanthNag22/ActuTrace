"""Additional illustrative ActuTrace tools; not production actuarial models."""
from math import isfinite


def compare_model_outputs(baseline: dict[str, float], candidate: dict[str, float], materiality_percent: float = 5.0) -> dict:
    if not 0 <= materiality_percent <= 100:
        raise ValueError("materiality_percent must be between 0 and 100.")
    if not baseline or set(baseline) != set(candidate):
        raise ValueError("Baseline and candidate must contain the same non-empty metric keys.")
    results = []
    for metric in sorted(baseline):
        old, new = float(baseline[metric]), float(candidate[metric])
        if not isfinite(old) or not isfinite(new):
            raise ValueError("Model outputs must be finite numbers.")
        delta = new - old
        pct = abs(delta) / abs(old) * 100 if old != 0 else (0.0 if new == 0 else 100.0)
        results.append({"metric": metric, "baseline": old, "candidate": new, "change": delta,
                        "absolute_change": abs(delta), "absolute_change_percent": pct,
                        "flagged": pct >= materiality_percent})
    results.sort(key=lambda row: row["absolute_change"], reverse=True)
    return {"tool": "model_change_monitor", "materiality_percent": materiality_percent,
            "flagged_metric_count": sum(row["flagged"] for row in results), "results": results,
            "data_basis": "User-supplied model outputs; this compares values and does not validate actuarial assumptions."}


def simulate_pricing(sum_assured: float, claim_probability: float, expense_load_percent: float, risk_load_percent: float) -> dict:
    values = (sum_assured, claim_probability, expense_load_percent, risk_load_percent)
    if not all(isfinite(v) for v in values):
        raise ValueError("All inputs must be finite numbers.")
    if sum_assured < 0:
        raise ValueError("sum_assured must be non-negative.")
    if not 0 <= claim_probability <= 1:
        raise ValueError("claim_probability must be between 0 and 1.")
    if not 0 <= expense_load_percent <= 500 or not 0 <= risk_load_percent <= 500:
        raise ValueError("Load percentages must be between 0 and 500.")
    expected = sum_assured * claim_probability
    expense = expected * expense_load_percent / 100
    risk = expected * risk_load_percent / 100
    return {"tool": "pricing_scenario_simulator", "inputs": {"sum_assured": sum_assured,
            "claim_probability": claim_probability, "expense_load_percent": expense_load_percent,
            "risk_load_percent": risk_load_percent}, "expected_claim_cost": expected,
            "expense_load": expense, "risk_load": risk, "illustrative_premium": expected + expense + risk,
            "data_basis": "Simplified scenario illustration only; not an approved pricing model or customer quote."}


def project_liability(starting_amount: float, annual_growth_percent: float, years: int) -> dict:
    if not isfinite(starting_amount) or starting_amount < 0:
        raise ValueError("starting_amount must be finite and non-negative.")
    if not isfinite(annual_growth_percent) or not -100 <= annual_growth_percent <= 100:
        raise ValueError("annual_growth_percent must be between -100 and 100.")
    if isinstance(years, bool) or not isinstance(years, int) or not 1 <= years <= 100:
        raise ValueError("years must be an integer between 1 and 100.")
    amount, schedule = starting_amount, []
    for year in range(1, years + 1):
        amount *= 1 + annual_growth_percent / 100
        schedule.append({"year": year, "projected_amount": amount})
    return {"tool": "liability_projection", "starting_amount": starting_amount,
            "annual_growth_percent": annual_growth_percent, "years": years,
            "schedule": schedule, "ending_amount": amount,
            "data_basis": "Deterministic growth scenario, not an actuarial reserve or liability valuation."}
