from fastapi import FastAPI

app = FastAPI(
    title="ActuTrace API",
    description="Life-insurance data quality and valuation-impact analysis",
    version="0.1.0",
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
    return {
        "status": "healthy",
    }
