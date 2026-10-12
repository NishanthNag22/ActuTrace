import csv
from pathlib import Path

REPORT_FIELDS = [
    "row_number",
    "policy_id",
    "field",
    "rule",
    "severity",
    "message",
]


def export_findings(findings: list[dict], output_path: str | Path) -> Path:
    """Export validation findings to a CSV report."""
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("w", newline="", encoding="utf-8-sig") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=REPORT_FIELDS)
        writer.writeheader()
        writer.writerows(findings)

    return path
