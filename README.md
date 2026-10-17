# ActuTrace

**An experimental actuarial workbench for policy-data quality, valuation-impact prioritisation, model-change review, and scenario exploration.**

ActuTrace explores a practical question: when policy data contains defects, which issues deserve attention first because of their potential financial impact? The platform combines policy-data validation with controlled synthetic valuation experiments and provides additional tools for comparing model outputs, exploring simplified pricing assumptions, projecting deterministic growth scenarios, and exporting reports.

> **Scope:** ActuTrace is a research and portfolio prototype. It uses synthetic data and simplified educational calculations; it is not a production actuarial valuation system. Outputs must not be used as actual insurer reserves, approved premiums, regulatory valuations, or financial advice.

## Features

### Core analysis
- **Policy Data Quality Validator** — detects configured missing, invalid, and duplicate policy-record issues.
- **Valuation Impact Analyzer** — runs configured defect scenarios against a clean synthetic baseline and measures changes in the implemented simplified model output.
- **Impact-based prioritisation** — ranks tested scenarios by absolute simulated impact while retaining the direction of change.
- **Materiality review** — flags tested scenarios against a configurable threshold.
- **Count-versus-impact comparison** — demonstrates how frequency-based and impact-based rankings can differ. The illustrative comparison is explicitly separated from measured experiment outputs.

### Additional workbench tools
- **Model Change Monitor** — compares baseline and candidate values for matching metric names, calculates absolute and percentage changes, and flags metrics at the selected percentage threshold.
- **Pricing Scenario Simulator** — calculates expected claim cost and adds configurable expense and risk loads using a simplified formula.
- **Liability Growth Projection** — applies a constant annual growth assumption to produce a deterministic year-by-year schedule.
- **Audit and Reporting** — exposes the generated analysis summary (JSON) and validation/valuation reports (CSV), where available.

### Engineering
- FastAPI backend and React + TypeScript frontend.
- Pytest coverage for validation, valuation workflow, ranking, API behavior, and the additional tool calculations.
- CSV and JSON outputs for inspection and reproducibility.

## Technology stack

| Layer | Technologies |
|---|---|
| Backend API | Python, FastAPI, Uvicorn, Pydantic |
| Data processing | Pandas and Python data-processing utilities |
| Frontend | React, TypeScript, Vite |
| Tests | Pytest |
| Version control | Git and GitHub |

## Repository structure

```text
ActuTrace/
├── backend/
│   ├── app/
│   │   ├── validation/
│   │   ├── valuation/
│   │   └── analysis_workflow.py
│   ├── tests/
│   ├── main.py
│   └── requirements.txt
├── data/
│   └── synthetic/
├── frontend/
│   ├── src/
│   ├── package.json
│   └── vite.config.ts
├── reports/
└── README.md
```

## Requirements

- Python version compatible with the packages in `backend/requirements.txt`
- Node.js and npm
- Git

## Run locally (Windows PowerShell)

Run commands from the repository root unless stated otherwise.

### 1. Create and activate a Python virtual environment

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
```

If PowerShell blocks activation, use Command Prompt and run `.venv\Scripts\activate.bat`, or use your already working Python environment.

### 2. Install backend dependencies

```powershell
python -m pip install -r backend\requirements.txt
```

### 3. Install frontend dependencies

Open a second terminal:

```powershell
cd frontend
npm install
```

### 4. Start the backend

From the repository root:

```powershell
python -m uvicorn backend.main:app --reload
```

API base URL: http://127.0.0.1:8000  
Interactive API documentation: http://127.0.0.1:8000/docs  
Health check: http://127.0.0.1:8000/health

### 5. Start the frontend

In another terminal:

```powershell
cd frontend
npm run dev
```

Open the local URL printed by Vite. Keep both servers running while using the application.

## Test and build

From the repository root, run the backend tests:

```powershell
python -m pytest backend\tests -v
```

Build the frontend:

```powershell
cd frontend
npm run build
```

Optional frontend lint:

```powershell
npm run lint
```

## How the valuation-impact experiment works

1. Load the configured synthetic policy dataset, clean baseline, and defect scenarios.
2. Run the clean baseline through the implemented simplified valuation model.
3. Apply a configured defect scenario and run the model again.
4. Compare the scenario output with the baseline and record the signed change.
5. Rank the tested scenarios by absolute impact so increases and decreases are compared by magnitude.
6. Compare the result with an illustrative count-based ranking and flag tested scenarios against the selected materiality threshold.

A validation finding is **not automatically assigned a financial impact**. Financial impact is measured only for the scenarios that are actually run through the implemented model. Effects from multiple defects may interact, so isolated scenario impacts should not be assumed to add up to a combined result.

## Additional tool calculations

- **Model Change Monitor:** percentage change is measured relative to the absolute baseline value. A non-zero candidate against a zero baseline is represented by the tool as a 100% change; interpret this edge case cautiously.
- **Pricing Scenario Simulator:** expected claim cost = sum assured × claim probability. Expense and risk loads are calculated as percentages of that expected claim cost, then added to it. This is a deliberately simplified illustration, not a complete premium calculation.
- **Liability Growth Projection:** each year multiplies the prior amount by (1 + annual growth rate). It does not model cash flows, mortality, discounting, policy duration, or actuarial assumptions.

## Limitations and responsible interpretation

- Uses synthetic policy data and simplified deterministic assumptions.
- Does not represent an insurer's production valuation, reserves, approved pricing, or regulatory reporting.
- The tested defect library is not exhaustive; a finding's financial impact is not known unless an appropriate scenario and model are used.
- Results depend on the implemented model, configured inputs, and selected scenarios.
- Isolated defect impacts may not add up to the combined impact when defects interact.
- Production use would require actuarial review, validated assumptions, secure data handling, stronger audit controls, and evaluation on representative data.
- The model-change tool compares numeric outputs; it does not establish that the underlying model or assumptions are correct.

## Future work

- Expand realistic defect classes and scenario coverage.
- Evaluate count-based versus impact-based prioritisation against known ground truth on larger controlled datasets.
- Strengthen interaction analysis and explain any residual between isolated and combined effects.
- Add more complete run/version metadata and reproducible experiment configuration.
- Improve automated end-to-end tests and dashboard error/empty states.
- Seek review from practising actuaries before making claims about real-world valuation usefulness.

## Disclaimer

ActuTrace is an experimental software project for learning, demonstration, and research. It is not a substitute for professional actuarial judgement, insurer controls, or regulatory valuation systems.
