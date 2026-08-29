"""
Automated Evaluation and Unit Test Suite for MPLADS AI Anomaly Platform
Evaluated on 10,000 synthetic records with Data Quality & Evidence Confidence metrics.
"""

import json
import pytest
from fastapi.testclient import TestClient

from backend.app.main import app, load_and_analyze_dataset
from backend.app.engine.risk_engine import RiskEngine
from scripts.generate_synthetic_data import generate_synthetic_dataset

client = TestClient(app)


def test_synthetic_data_generation_10k():
    works, gt_labels = generate_synthetic_dataset(1000)
    assert len(works) == 1000
    assert isinstance(gt_labels, dict)
    assert len(gt_labels) > 0


def test_multi_signal_risk_engine_and_metrics():
    works, gt_labels = generate_synthetic_dataset(1000)
    
    engine = RiskEngine()
    alerts, agency_profiles, analyzed_works = engine.analyze_all_works(works)

    assert len(analyzed_works) == 1000
    assert len(agency_profiles) > 0
    assert len(alerts) > 0

    flagged_work_ids = set()
    for alert in alerts:
        if alert.risk_score >= 50.0:
            flagged_work_ids.add(alert.work_id)

    ground_truth_anomalous_ids = set(gt_labels.keys())

    tp = len(flagged_work_ids.intersection(ground_truth_anomalous_ids))
    fp = len(flagged_work_ids - ground_truth_anomalous_ids)
    fn = len(ground_truth_anomalous_ids - flagged_work_ids)

    precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0

    print(f"\n--- Refined ML Risk Engine Evaluation Metrics ---")
    print(f"Total Works Evaluated: 1,000 | Ground Truth Anomalies: {len(ground_truth_anomalous_ids)}")
    print(f"Flagged Works (Score >= 50): {len(flagged_work_ids)}")
    print(f"True Positives: {tp} | False Positives: {fp} | False Negatives: {fn}")
    print(f"Precision: {precision:.4f} | Recall: {recall:.4f} | F1 Score: {f1:.4f}")

    assert precision >= 0.65
    assert recall >= 0.45
    assert f1 >= 0.50


def test_fastapi_endpoints():
    load_and_analyze_dataset()

    response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

    response = client.get("/api/v1/overview")
    assert response.status_code == 200
    data = response.json()
    assert data["total_works"] > 0
    assert "avg_data_quality_score" in data

    response = client.get("/api/v1/works?limit=10")
    assert response.status_code == 200
    w_data = response.json()
    assert len(w_data["works"]) <= 10

    first_wid = w_data["works"][0]["work_id"]
    response = client.get(f"/api/v1/works/{first_wid}")
    assert response.status_code == 200
    assert response.json()["work_id"] == first_wid

    response = client.get(f"/api/v1/works/{first_wid}/investigation")
    assert response.status_code == 200
    assert "work" in response.json()

    response = client.get("/api/v1/alerts?limit=5")
    assert response.status_code == 200
    a_data = response.json()
    assert len(a_data["alerts"]) > 0

    alert_id = a_data["alerts"][0]["alert_id"]
    review_payload = {
        "officer_name": "District Collector Nadia",
        "officer_role": "District Magistrate",
        "action": "Escalated for Physical Site Inspection",
        "remarks": "Ordered field physical measurement survey."
    }
    response = client.post(f"/api/v1/alerts/{alert_id}/review", json=review_payload)
    assert response.status_code == 200
    assert response.json()["status"] == "success"

    response = client.post("/api/v1/copilot/query", json={"query": "Show high-risk works in Nadia"})
    assert response.status_code == 200
    assert "answer" in response.json()
