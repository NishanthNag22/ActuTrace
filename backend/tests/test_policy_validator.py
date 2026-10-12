
from pathlib import Path

from backend.app.validation.policy_validator import validate_policies


PROJECT_ROOT = Path(__file__).resolve().parents[2]
POLICY_FILE = PROJECT_ROOT / "data" / "synthetic" / "policies.csv"


def test_validator_returns_findings():
    findings = validate_policies(POLICY_FILE)

    assert len(findings) > 0


def test_missing_date_of_birth_is_detected():
    findings = validate_policies(POLICY_FILE)

    matching = [
        finding
        for finding in findings
        if finding["policy_id"] == "P1004"
        and finding["field"] == "date_of_birth"
        and finding["rule"] == "MISSING_REQUIRED_VALUE"
    ]

    assert len(matching) == 1


def test_negative_sum_assured_is_detected():
    findings = validate_policies(POLICY_FILE)

    matching = [
        finding
        for finding in findings
        if finding["policy_id"] == "P1005"
        and finding["field"] == "sum_assured"
        and finding["rule"] == "NEGATIVE_VALUE"
    ]

    assert len(matching) == 1


def test_both_duplicate_policy_records_are_flagged():
    findings = validate_policies(POLICY_FILE)

    matching = [
        finding
        for finding in findings
        if finding["policy_id"] == "P1002"
        and finding["rule"] == "DUPLICATE_POLICY_ID"
    ]

    assert len(matching) == 2


def test_invalid_policy_status_is_detected():
    findings = validate_policies(POLICY_FILE)

    assert any(
        f["policy_id"] == "P1008"
        and f["rule"] == "INVALID_POLICY_STATUS"
        for f in findings
    )


def test_future_date_of_birth_is_detected():
    findings = validate_policies(POLICY_FILE)

    assert any(
        f["policy_id"] == "P1012"
        and f["rule"] == "FUTURE_DATE_OF_BIRTH"
        for f in findings
    )


def test_zero_policy_term_is_detected():
    findings = validate_policies(POLICY_FILE)

    assert any(
        f["policy_id"] == "P1013"
        and f["rule"] == "ZERO_POLICY_TERM"
        for f in findings
    )


def test_zero_sum_assured_is_detected():
    findings = validate_policies(POLICY_FILE)

    assert any(
        f["policy_id"] == "P1014"
        and f["rule"] == "ZERO_SUM_ASSURED"
        for f in findings
    )
