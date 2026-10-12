
import pytest

from backend.app.valuation.valuation_model import (
    estimate_expected_claim_cost,
    estimate_portfolio_expected_cost,
    estimate_simple_claim_amount,
)


def test_estimate_claim_amount():
    assert estimate_simple_claim_amount(500000) == 500000.0


def test_zero_sum_assured_returns_zero():
    assert estimate_simple_claim_amount(0) == 0.0


def test_negative_sum_assured_raises_error():
    with pytest.raises(ValueError, match="cannot be negative"):
        estimate_simple_claim_amount(-250000)


def test_expected_claim_cost():
    assert estimate_expected_claim_cost(500000, 0.02) == 10000.0


def test_zero_claim_probability_returns_zero():
    assert estimate_expected_claim_cost(500000, 0) == 0.0


def test_claim_probability_cannot_exceed_one():
    with pytest.raises(ValueError, match="between 0 and 1"):
        estimate_expected_claim_cost(500000, 1.5)


def test_negative_claim_probability_is_rejected():
    with pytest.raises(ValueError, match="between 0 and 1"):
        estimate_expected_claim_cost(500000, -0.1)


def test_portfolio_expected_cost():
    policies = [
        {"sum_assured": 500000},
        {"sum_assured": 300000},
    ]

    result = estimate_portfolio_expected_cost(policies, 0.02)

    assert result == 16000.0


def test_empty_portfolio_returns_zero():
    assert estimate_portfolio_expected_cost([], 0.02) == 0.0


def test_portfolio_rejects_negative_sum_assured():
    policies = [{"sum_assured": -100000}]

    with pytest.raises(ValueError, match="cannot be negative"):
        estimate_portfolio_expected_cost(policies, 0.02)


def test_portfolio_requires_sum_assured():
    policies = [{"policy_id": "P1001"}]

    with pytest.raises(ValueError, match="must contain sum_assured"):
        estimate_portfolio_expected_cost(policies, 0.02)
