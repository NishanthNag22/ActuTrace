
from pathlib import Path

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from backend.app.analysis_workflow import run_actutrace_analysis


# Locate the project root, regardless of the terminal's current directory.
PROJECT_ROOT = Path(__file__).resolve().parent.parent

POLICY_FILE = PROJECT_ROOT / "data" / "synthetic" / "policies.csv"
CLEAN_BASELINE_FILE = (
    PROJECT_ROOT / "data" / "synthetic" / "clean_policies.csv"
)
SCENARIO_FILE = (
    PROJECT_ROOT / "data" / "synthetic" / "defect_scenarios.json"
)
OUTPUT_DIRECTORY = PROJECT_ROOT / "reports" / "analysis"


app = FastAPI(
    title="ActuTrace API",
    description=(
        "Life-insurance data quality validation and "
        "valuation-impact analysis."
    ),
    version="0.2.0",
)


class AnalysisRequest(BaseModel):
    claim_probability: float = Field(default=0.02, gt=0, le=1)
    materiality_threshold_percent: float = Field(
        default=5.0, gt=0, le=100
    )


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
            materiality_threshold_percent=(
                request.materiality_threshold_percent
            ),
        )
        return result

    except (ValueError, FileNotFoundError) as error:
        raise HTTPException(
            status_code=400,
            detail=str(error),
        ) from error
