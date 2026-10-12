
import json
from pathlib import Path


REQUIRED_FIELDS = {
    "defect_id",
    "policy_id",
    "field",
    "original_value",
    "altered_value",
    "description",
}


def load_defect_scenarios(
    json_path: str | Path,
) -> list[dict]:
    """Load and validate controlled defect scenarios from JSON."""
    path = Path(json_path)

    with path.open("r", encoding="utf-8") as json_file:
        scenarios = json.load(json_file)

    if not isinstance(scenarios, list):
        raise ValueError("Scenario file must contain a JSON list.")

    seen_ids = set()

    for scenario in scenarios:
        if not isinstance(scenario, dict):
            raise ValueError("Every scenario must be a JSON object.")

        missing_fields = REQUIRED_FIELDS - scenario.keys()

        if missing_fields:
            missing = ", ".join(sorted(missing_fields))
            raise ValueError(f"Scenario is missing fields: {missing}")

        defect_id = scenario["defect_id"]

        if not isinstance(defect_id, str) or not defect_id.strip():
            raise ValueError("Each defect_id must be a non-empty string.")

        if defect_id in seen_ids:
            raise ValueError(f"Duplicate defect_id: {defect_id}")

        seen_ids.add(defect_id)

        if scenario["field"] != "sum_assured":
            raise ValueError(
                "Only sum_assured scenarios are currently supported."
            )

        for field in ("original_value", "altered_value"):
            value = scenario[field]

            if isinstance(value, bool) or not isinstance(value, (int, float)):
                raise ValueError(f"{field} must be numeric.")

            if value < 0:
                raise ValueError(f"{field} cannot be negative.")

        if scenario["original_value"] == scenario["altered_value"]:
            raise ValueError(
                "Original and altered values must be different."
            )

    return scenarios
