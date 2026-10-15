from pathlib import Path

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from backend.app.analysis_workflow import run_actutrace_analysis
from backend.app.valuation.priority_comparator import compare_priority_methods
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

# Locate the project root, regardless of the terminal's current directory.
PROJECT_ROOT = Path(__file__).resolve().parent.parent

POLICY_FILE = PROJECT_ROOT / "data" / "synthetic" / "policies.csv"
CLEAN_BASELINE_FILE = PROJECT_ROOT / "data" / "synthetic" / "clean_policies.csv"
SCENARIO_FILE = PROJECT_ROOT / "data" / "synthetic" / "defect_scenarios.json"
OUTPUT_DIRECTORY = PROJECT_ROOT / "reports" / "analysis"


app = FastAPI(
    title="ActuTrace API",
    description=(
        "Life-insurance data quality validation and " "valuation-impact analysis."
    ),
    version="0.2.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)


class AnalysisRequest(BaseModel):
    claim_probability: float = Field(default=0.02, gt=0, le=1)
    materiality_threshold_percent: float = Field(default=5.0, gt=0, le=100)


@app.get("/")
def home():
    return {
        "application": "ActuTrace",
        "message": "Welcome to ActuTrace",
        "status": "running",
    }


@app.get("/health")
def health_check():
    return {"status": "healthy"}


import csv


def read_csv_report(path: Path) -> list[dict]:
    if not path.is_file():
        return []

    with path.open("r", encoding="utf-8-sig", newline="") as csv_file:
        return list(csv.DictReader(csv_file))


@app.post("/analysis")
def run_analysis(request: AnalysisRequest):
    required_files = [
        POLICY_FILE,
        CLEAN_BASELINE_FILE,
        SCENARIO_FILE,
    ]

    missing_files = [
        str(path.relative_to(PROJECT_ROOT))
        for path in required_files
        if not path.is_file()
    ]

    if missing_files:
        raise HTTPException(
            status_code=500,
            detail={
                "message": "Required analysis data files are missing.",
                "missing_files": missing_files,
            },
        )

    try:
        result = run_actutrace_analysis(
            policy_csv_path=POLICY_FILE,
            clean_baseline_csv_path=CLEAN_BASELINE_FILE,
            scenario_json_path=SCENARIO_FILE,
            output_directory=OUTPUT_DIRECTORY,
            claim_probability=request.claim_probability,
            materiality_threshold_percent=(request.materiality_threshold_percent),
        )
        result["validation_findings"] = read_csv_report(
            OUTPUT_DIRECTORY / "validation_findings.csv"
        )
        result["valuation_impacts"] = read_csv_report(
            OUTPUT_DIRECTORY / "valuation_impacts.csv"
        )

        return result

    except (ValueError, FileNotFoundError) as error:
        raise HTTPException(
            status_code=400,
            detail=str(error),
        ) from error


@app.get("/reports/{report_name}")
def download_report(report_name: str):
    allowed_reports = {
        "validation_findings.csv": (OUTPUT_DIRECTORY / "validation_findings.csv"),
        "valuation_impacts.csv": (OUTPUT_DIRECTORY / "valuation_impacts.csv"),
    }

    report_path = allowed_reports.get(report_name)

    if report_path is None:
        raise HTTPException(
            status_code=404,
            detail="Report not found.",
        )

    if not report_path.is_file():
        raise HTTPException(
            status_code=404,
            detail="Run an analysis before downloading this report.",
        )

    return FileResponse(
        path=report_path,
        media_type="text/csv",
        filename=report_name,
    )


@app.get("/priority-comparison")
def get_priority_comparison():
    # Controlled synthetic example: occurrence frequency and impact
    # are deliberately different so the ranking methods can be compared.
    synthetic_defects = [
        {"defect_type": "Missing dates", "impact": -100},
        {"defect_type": "Missing dates", "impact": -100},
        {"defect_type": "Missing dates", "impact": -100},
        {"defect_type": "Invalid status", "impact": -300},
        {"defect_type": "Incorrect sum assured", "impact": -5000},
    ]

    result = compare_priority_methods(synthetic_defects)
    result["data_basis"] = (
        "Controlled synthetic example; not measured impacts from "
        "the validation findings report."
    )
    return result


@app.get("/measured-priority")
def get_measured_priority():
    """Rank the actual controlled valuation experiment by measured impact."""
    report_path = OUTPUT_DIRECTORY / "valuation_impacts.csv"
    if not report_path.exists():
        raise HTTPException(
            status_code=404,
            detail="Run the analysis before requesting measured priorities.",
        )

    with report_path.open("r", newline="", encoding="utf-8") as csv_file:
        rows = list(csv.DictReader(csv_file))

    results = []
    for row in rows:
        try:
            impact = float(row["impact"])
        except (KeyError, ValueError) as exc:
            raise HTTPException(
                status_code=500,
                detail="The valuation impact report has an invalid format.",
            ) from exc

        results.append(
            {
                "defect_id": row.get("defect_id", ""),
                "policy_id": row.get("policy_id", ""),
                "impact": impact,
                "absolute_impact": abs(impact),
            }
        )

    results.sort(key=lambda item: item["absolute_impact"], reverse=True)

    for rank, item in enumerate(results, start=1):
        item["rank"] = rank

    return {
        "data_basis": (
            "Measured outputs from the controlled synthetic valuation "
            "experiment; not production actuarial estimates."
        ),
        "results": results,
    }
