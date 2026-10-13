
from fastapi.testclient import TestClient

from backend import main


client = TestClient(main.app)


def test_home_endpoint():
    response = client.get("/")

    assert response.status_code == 200
    assert response.json()["application"] == "ActuTrace"


def test_health_endpoint():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_analysis_endpoint(monkeypatch):
    expected_result = {
        "application": "ActuTrace",
        "validation": {
            "finding_count": 10,
            "severity_counts": {"high": 8, "medium": 2},
        },
        "valuation": {
            "defect_count": 2,
            "material_defect_count": 2,
        },
    }

    def fake_analysis(**kwargs):
        assert kwargs["claim_probability"] == 0.02
        assert kwargs["materiality_threshold_percent"] == 5.0
        return expected_result

    monkeypatch.setattr(
        main,
        "run_actutrace_analysis",
        fake_analysis,
    )

    response = client.post("/analysis", json={})

    assert response.status_code == 200
    assert response.json() == expected_result


def test_analysis_rejects_invalid_probability():
    response = client.post(
        "/analysis",
        json={"claim_probability": 0},
    )

    assert response.status_code == 422


def test_analysis_rejects_invalid_materiality_threshold():
    response = client.post(
        "/analysis",
        json={"materiality_threshold_percent": 101},
    )

    assert response.status_code == 422
