
import csv
from pathlib import Path


IMPACT_REPORT_FIELDS = [
    "rank",
    "defect_id",
    "policy_id",
    "field",
    "original_value",
    "altered_value",
    "impact",
    "absolute_impact",
    "impact_percent",
    "is_material",
]


def export_impact_results(
    ranked_defects: list[dict],
    output_path: str | Path,
) -> Path:
    """Export ranked simulated valuation impacts to a CSV file."""
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open(
        "w",
        newline="",
        encoding="utf-8-sig",
    ) as csv_file:
        writer = csv.DictWriter(
            csv_file,
            fieldnames=IMPACT_REPORT_FIELDS,
            extrasaction="ignore",
        )
        writer.writeheader()

        for rank, defect in enumerate(ranked_defects, start=1):
            writer.writerow({
                "rank": rank,
                **defect,
            })

    return path
