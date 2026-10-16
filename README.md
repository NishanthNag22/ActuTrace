# ActuTrace

ActuTrace is a prototype actuarial data-quality and valuation-impact analysis platform. It identifies policy-data defects, runs controlled valuation experiments, and prioritizes tested defects by their measured financial impact within a simplified valuation model.

## Key Features

- **Policy data validation:** Detects missing fields, invalid values, and duplicate policy records.
- **Controlled defect experiments:** Applies predefined defects to synthetic policy data and compares the results with a clean baseline.
- **Valuation-impact analysis:** Measures changes in model output associated with tested defect scenarios.
- **Impact-based prioritization:** Ranks tested scenarios by the absolute magnitude of their simulated financial impact while preserving the signed impact.
- **Priority comparison:** Illustrates how count-based and impact-based rankings can differ.
- **Dashboard:** Presents validation findings, valuation priorities, and analysis results.
- **Report exports:** Generates CSV and JSON reports.
- **Automated tests:** Tests validation, valuation workflows, ranking logic, and API error handling.

## Technology Stack

**Backend**
- Python
- FastAPI
- Uvicorn
- Pandas
- Pytest

**Frontend**
- React
- TypeScript
- Vite

## Project Structure

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
│       ├── clean_policies.csv
│       ├── defect_scenarios.json
│       └── policies.csv
├── frontend/
│   ├── src/
│   ├── package.json
│   └── vite.config.ts
├── reports/
│   └── validation_findings.csv
└── README.md
```

## Prerequisites

Install the following:

- Python 3.14, or a compatible Python version supported by the dependencies
- Node.js and npm
- Git

## Setup

Run these commands from the project root.

### 1. Create and activate the Python environment

```powershell
py -m venv backend\venv
.\backend\venv\Scripts\Activate.ps1
```

If the virtual environment already exists, activate it without recreating it.

### 2. Install backend dependencies

```powershell
python -m pip install -r backend\requirements.txt
```

### 3. Install frontend dependencies

Open a second terminal at the project root and run:

```powershell
cd frontend
npm install
```

## Run the Application

### Start the backend

From the project root, with the backend virtual environment activated, run:

```powershell
python -m uvicorn backend.main:app --reload
```

The API is available at:

- API: http://127.0.0.1:8000
- Interactive API documentation: http://127.0.0.1:8000/docs

### Start the frontend

In a separate terminal, run:

```powershell
cd frontend
npm run dev
```

Open the local URL printed by Vite. Keep both servers running while using the dashboard.

## Run Tests and Build

Run backend tests from the project root:

```powershell
python -m pytest backend\tests -v
```

Build the frontend for production:

```powershell
cd frontend
npm run build
```

Run the frontend linter:

```powershell
npm run lint
```

## How Valuation-Impact Prioritization Works

1. Load synthetic policy data and predefined defect scenarios.
2. Run the clean baseline through the simplified valuation model.
3. Apply a selected defect scenario and run the model again.
4. Compare the scenario result with the baseline.
5. Record the measured change in model output.
6. Rank tested scenarios by the absolute magnitude of their measured impact.

The signed impact indicates the direction of change. Absolute impact is used to rank scenarios by magnitude, whether the model output increases or decreases.

## Interpreting Results

ActuTrace distinguishes between two types of prioritization output.

**Measured valuation priorities**

These results come from running configured defect scenarios through the implemented valuation experiment. They depend on the synthetic data and model assumptions.

**Illustrative priority comparison**

This controlled example demonstrates why ranking defects by count can differ from ranking them by financial impact. It is not the measured ranking of all validation findings.

A validation finding is not automatically assigned a financial impact. Quantifying that impact requires an appropriate model or a defensible mapping.

## Current Limitations

- ActuTrace is a research and portfolio prototype, not a production actuarial valuation system.
- It uses synthetic policy data and a simplified valuation model.
- Measured impacts apply only to the scenarios tested and the assumptions configured in the model.
- Outputs are not actual insurer reserves, regulatory valuations, or financial advice.
- Individual defect effects may interact, so isolated impacts do not necessarily add up to the combined impact.
- The current experiment does not establish that every possible policy-data defect has been detected or financially quantified.
- Production use would require actuarial review, validated assumptions, stronger data governance, and testing with representative real-world data.

## Future Improvements

- Expand the library of realistic defect scenarios.
- Add materiality thresholds based on a clearly defined valuation measure.
- Quantify interactions between defects and report any unexplained residual.
- Evaluate prioritization against ground-truth financial impacts across larger test datasets.
- Improve reproducibility, audit trails, and report metadata.
- Validate the approach with practising actuaries and representative data.

## Disclaimer

ActuTrace is an experimental software project intended for demonstration and research. Its outputs must not be used as a substitute for professional actuarial judgment or production valuation controls.
