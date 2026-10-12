
import csv

from backend.app.validation.report_exporter import export_findings


def test_export_findings_creates_csv_with_headers(tmp_path):
    output_file = tmp_path / "validation_findings.csv"

    export_findings([], output_file)

    assert output_file.exists()

    with output_file.open(
        "r", newline="", encoding="utf-8-sig"
    ) as csv_file:
        reader = csv.DictReader(csv_file)
        assert reader.fieldnames == [
            "row_number",
            "policy_id",
            "field",
            "rule",
            "severity",
            "message",
        ]


def test_export_findings_writes_all_findings(tmp_path):
    output_file = tmp_path / "validation_findings.csv"

    findings = [
        {
            "row_number": 5,
            "policy_id": "P1004",
            "field": "date_of_birth",
            "rule": "MISSING_REQUIRED_VALUE",
            "severity": "high",
            "message": "Date of birth is missing.",
        },
        {
            "row_number": 6,
            "policy_id": "P1005",
            "field": "sum_assured",
            "rule": "NEGATIVE_VALUE",
            "severity": "high",
            "message": "Sum assured cannot be negative.",
        },
    ]

    export_findings(findings, output_file)

    with output_file.open(
        "r", newline="", encoding="utf-8-sig"
    ) as csv_file:
        rows = list(csv.DictReader(csv_file))

    assert len(rows) == 2
    assert rows[0]["policy_id"] == "P1004"
    assert rows[1]["rule"] == "NEGATIVE_VALUE"
