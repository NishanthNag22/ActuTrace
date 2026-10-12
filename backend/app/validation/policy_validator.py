from pathlib import Path

import pandas as pd

REQUIRED_COLUMNS = [
    "policy_id",
    "date_of_birth",
    "policy_start_date",
    "policy_term_years",
    "sum_assured",
    "annual_premium",
    "policy_status",
]

ALLOWED_STATUSES = {"active", "lapsed", "matured", "cancelled"}


def validate_policies(csv_path: str | Path) -> list[dict]:
    """Read a policy CSV and return a list of data-quality findings."""
    df = pd.read_csv(csv_path, dtype={"policy_id": "string"})

    missing_columns = [
        column for column in REQUIRED_COLUMNS if column not in df.columns
    ]
    if missing_columns:
        raise ValueError(
            f"CSV is missing required columns: {', '.join(missing_columns)}"
        )

    findings = []

    def add_finding(
        row_number: int,
        policy_id: str,
        field: str,
        rule: str,
        severity: str,
        message: str,
    ) -> None:
        findings.append(
            {
                "row_number": row_number,
                "policy_id": policy_id,
                "field": field,
                "rule": rule,
                "severity": severity,
                "message": message,
            }
        )

    # Check each policy record. CSV row numbers include the header row.
    for index, row in df.iterrows():
        row_number = index + 2
        policy_id = row["policy_id"]

        if pd.isna(policy_id) or not str(policy_id).strip():
            policy_id = "<missing>"
            add_finding(
                row_number,
                policy_id,
                "policy_id",
                "MISSING_POLICY_ID",
                "high",
                "Policy ID is missing.",
            )

        for field in REQUIRED_COLUMNS:
            if field != "policy_id" and pd.isna(row[field]):
                add_finding(
                    row_number,
                    str(policy_id),
                    field,
                    "MISSING_REQUIRED_VALUE",
                    "high",
                    f"Required field '{field}' is missing.",
                )

        # Validate dates.
        dob = pd.to_datetime(row["date_of_birth"], errors="coerce")
        start_date = pd.to_datetime(row["policy_start_date"], errors="coerce")

        if pd.notna(row["date_of_birth"]) and pd.isna(dob):
            add_finding(
                row_number,
                str(policy_id),
                "date_of_birth",
                "INVALID_DATE",
                "high",
                "Date of birth is invalid.",
            )
        elif pd.notna(dob) and dob > pd.Timestamp.today().normalize():
            add_finding(
                row_number,
                str(policy_id),
                "date_of_birth",
                "FUTURE_DATE_OF_BIRTH",
                "high",
                "Date of birth cannot be in the future.",
            )

        if pd.notna(row["policy_start_date"]) and pd.isna(start_date):
            add_finding(
                row_number,
                str(policy_id),
                "policy_start_date",
                "INVALID_DATE",
                "high",
                "Policy start date is invalid.",
            )

        # Validate numeric fields.
        for field in ["policy_term_years", "sum_assured", "annual_premium"]:
            value = pd.to_numeric(row[field], errors="coerce")

            if pd.notna(row[field]) and pd.isna(value):
                add_finding(
                    row_number,
                    str(policy_id),
                    field,
                    "INVALID_NUMBER",
                    "high",
                    f"Field '{field}' must contain a number.",
                )
            elif pd.notna(value) and value < 0:
                add_finding(
                    row_number,
                    str(policy_id),
                    field,
                    "NEGATIVE_VALUE",
                    "high",
                    f"Field '{field}' cannot be negative.",
                )
            elif field == "policy_term_years" and pd.notna(value) and value == 0:
                add_finding(
                    row_number,
                    str(policy_id),
                    field,
                    "ZERO_POLICY_TERM",
                    "high",
                    "Policy term must be greater than zero.",
                )
            elif field == "sum_assured" and pd.notna(value) and value == 0:
                add_finding(
                    row_number,
                    str(policy_id),
                    field,
                    "ZERO_SUM_ASSURED",
                    "medium",
                    "Sum assured is zero; verify whether this is permitted.",
                )

        # Validate policy status.
        status = row["policy_status"]
        if pd.notna(status) and str(status).strip().lower() not in ALLOWED_STATUSES:
            add_finding(
                row_number,
                str(policy_id),
                "policy_status",
                "INVALID_POLICY_STATUS",
                "medium",
                f"Unsupported policy status: {status}.",
            )

        # A policy start date must not precede the date of birth.
        if pd.notna(dob) and pd.notna(start_date) and start_date < dob:
            add_finding(
                row_number,
                str(policy_id),
                "policy_start_date",
                "START_BEFORE_BIRTH",
                "high",
                "Policy start date precedes date of birth.",
            )

    # Flag every occurrence of a duplicated, non-empty policy ID.
    valid_ids = df["policy_id"].dropna().astype(str).str.strip()
    duplicated_ids = set(valid_ids[valid_ids.duplicated(keep=False)])

    for index, row in df.iterrows():
        policy_id = row["policy_id"]
        if pd.notna(policy_id) and str(policy_id).strip() in duplicated_ids:
            add_finding(
                index + 2,
                str(policy_id),
                "policy_id",
                "DUPLICATE_POLICY_ID",
                "high",
                f"Policy ID '{policy_id}' appears more than once.",
            )

    return findings
