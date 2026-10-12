
import json
from pathlib import Path

from backend.app.validation.policy_validator import validate_policies
from backend.app.validation.report_exporter import export_findings
from backend.app.valuation.experiment_runner import run_scenario_file
from backend.app.valuation.valuation_report_exporter import (
    export_impact_results,
)


def run_actutrace_analysis(
    policy_csv_path: str | Path,
    clean_baseline_csv_path: str | Path,
    scenario_json_path: str | Path,
    output_directory: str | Path,
    claim_probability: float = 0.02,
    materiality_threshold_percent: float = 5.0,
) -> dict:
    """
    Run validation and controlled valuation analysis.

    The policy CSV is validated independently from the trusted clean
    baseline used for the controlled valuation experiment.
    """
    output_dir = Path(output_directory)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Stage 1: Find data-quality issues in the supplied policy dataset.
    findings = validate_policies(policy_csv_path)

    findings_path = export_findings(
        findings,
        output_dir / "validation_findings.csv",
    )

    severity_counts = {}
    for finding in findings:
        severity = finding["severity"]
        severity_counts[severity] = severity_counts.get(severity, 0) + 1

    # Stage 2: Run the controlled experiment against its trusted baseline.
    valuation = run_scenario_file(
        clean_csv_path=clean_baseline_csv_path,
        scenario_json_path=scenario_json_path,
        claim_probability=claim_probability,
        materiality_threshold_percent=materiality_threshold_percent,
    )

    impacts_path = export_impact_results(
        valuation["ranked_defects"],
        output_dir / "valuation_impacts.csv",
    )

    # Stage 3: Produce a compact summary for dashboards and APIs.
    summary = {
        "application": "ActuTrace",
        "validation": {
            "finding_count": len(findings),
            "severity_counts": severity_counts,
            "report_path": str(findings_path),
        },
        "valuation": {
            "baseline_expected_cost": valuation["baseline_expected_cost"],
            "claim_probability": valuation["claim_probability"],
            "defect_count": valuation["defect_count"],
            "material_defect_count": valuation["material_defect_count"],
            "combined_impact": valuation["combined_impact"],
            "sum_isolated_impacts": valuation["sum_isolated_impacts"],
            "interaction_residual": valuation["interaction_residual"],
            "materiality_threshold_percent": (
                valuation["materiality_threshold_percent"]
            ),
            "report_path": str(impacts_path),
            "valuation_basis": valuation["valuation_basis"],
        },
        "interpretation": (
            "Validation findings describe data-quality issues. "
            "Valuation impacts describe controlled simulated scenarios. "
            "They are related reports, but they are not a one-to-one "
            "mapping of every finding to a financial impact."
        ),
    }

    summary_path = output_dir / "analysis_summary.json"
    with summary_path.open("w", encoding="utf-8") as json_file:
        json.dump(summary, json_file, indent=2)

    summary["summary_path"] = str(summary_path)

    return summary
