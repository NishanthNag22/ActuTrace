
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


def test_priority_comparison_endpoint():
    response = client.get("/priority-comparison")

    assert response.status_code == 200

    result = response.json()
    assert result["defect_type_count"] == 3
    assert result["ranking_differs"] is True
    assert len(result["results"]) == 3
    assert "synthetic" in result["data_basis"].lower()


def test_measured_priority_endpoint(monkeypatch, tmp_path):
    report_path = tmp_path / "valuation_impacts.csv"
    report_path.write_text(
        "defect_id,policy_id,impact\n"
        "D001,P1001,-2000\n"
        "D002,P1002,-4000\n",
        encoding="utf-8",
    )

    monkeypatch.setattr(
        main,
        "OUTPUT_DIRECTORY",
        tmp_path,
    )

    response = client.get("/measured-priority")

    assert response.status_code == 200
    result = response.json()
    assert len(result["results"]) == 2
    assert result["results"][0]["defect_id"] == "D002"
    assert result["results"][0]["absolute_impact"] == 4000
    assert result["results"][0]["rank"] == 1
    assert "controlled synthetic valuation experiment" in (
        result["data_basis"]
    )


def test_measured_priority_missing_report_returns_404(
    monkeypatch,
    tmp_path,
):
    monkeypatch.setattr(
        main,
        "OUTPUT_DIRECTORY",
        tmp_path,
    )

    response = client.get("/measured-priority")

    assert response.status_code == 404


def test_measured_priority_malformed_report_returns_500(
    monkeypatch,
    tmp_path,
):
    report_path = tmp_path / "valuation_impacts.csv"
    report_path.write_text(
        "defect_id,policy_id\nD001,P1001\n",
        encoding="utf-8",
    )

    monkeypatch.setattr(
        main,
        "OUTPUT_DIRECTORY",
        tmp_path,
    )

    response = client.get("/measured-priority")

    assert response.status_code == 500
    assert "invalid format" in response.json()["detail"].lower()
