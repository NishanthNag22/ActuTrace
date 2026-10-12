
import csv
from pathlib import Path

from backend.app.valuation.defect_experiment import (
    run_defect_experiment,
)
from backend.app.valuation.scenario_loader import (
    load_defect_scenarios,
)


def load_clean_policies(csv_path: str | Path) -> list[dict]:
    """Load the trusted baseline portfolio from a CSV file."""
    with Path(csv_path).open(
        "r",
        newline="",
        encoding="utf-8-sig",
    ) as csv_file:
        reader = csv.DictReader(csv_file)

        required_columns = {"policy_id", "sum_assured"}
        if not reader.fieldnames or not required_columns.issubset(
            reader.fieldnames
        ):
            raise ValueError(
                "Clean portfolio CSV must contain policy_id and sum_assured."
            )

        policies = []
        seen_ids = set()

        for row in reader:
            policy_id = row["policy_id"]

            if not policy_id or not policy_id.strip():
                raise ValueError("Clean portfolio contains an empty policy_id.")

            if policy_id in seen_ids:
                raise ValueError(
                    f"Clean portfolio contains duplicate policy ID: {policy_id}"
                )

            seen_ids.add(policy_id)

            try:
                sum_assured = float(row["sum_assured"])
            except (TypeError, ValueError) as error:
                raise ValueError(
                    f"Invalid sum_assured for policy {policy_id!r}."
                ) from error

            if sum_assured < 0:
                raise ValueError(
                    f"Negative sum_assured for policy {policy_id!r}."
                )

            policies.append(
                {
                    "policy_id": policy_id,
                    "sum_assured": sum_assured,
                }
            )

    return policies


def run_scenario_file(
    clean_csv_path: str | Path,
    scenario_json_path: str | Path,
    claim_probability: float = 0.02,
    materiality_threshold_percent: float = 5.0,
) -> dict:
    """Load a trusted baseline and run its controlled scenarios."""
    clean_policies = load_clean_policies(clean_csv_path)
    scenarios = load_defect_scenarios(scenario_json_path)

    baseline_by_id = {
        policy["policy_id"]: policy for policy in clean_policies
    }

    for scenario in scenarios:
        policy = baseline_by_id.get(scenario["policy_id"])

        if policy is None:
            raise ValueError(
                f"Scenario references unknown policy "
                f"{scenario['policy_id']!r}."
            )

        if float(scenario["original_value"]) != policy["sum_assured"]:
            raise ValueError(
                f"Scenario {scenario['defect_id']!r} original_value "
                f"does not match the clean baseline."
            )

    return run_defect_experiment(
        clean_policies=clean_policies,
        defects=scenarios,
        claim_probability=claim_probability,
        materiality_threshold_percent=materiality_threshold_percent,
    )
