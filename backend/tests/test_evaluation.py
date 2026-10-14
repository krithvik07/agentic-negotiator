import requests
import numpy as np
from fastapi.testclient import TestClient
from app.main import app
from app.evaluation.metrics import calculate_all_metrics

client = TestClient(app)

def test_record_negotiation_outcome():
    # Test data
    test_outcome = {
        "session_id": "test-session-123",
        "accepted": True,
        "predicted_prob": 0.85,
        "features": {
            "initial_price": 1000,
            "final_price": 900,
            "rounds": 3
        }
    }
    
    # Record outcome
    response = client.post(
        "/negotiation/record-outcome",
        json=test_outcome
    )
    assert response.status_code == 200
    assert response.json()["status"] == "success"

def test_generate_evaluation_report():
    # Generate report
    response = client.get("/evaluation/report")
    assert response.status_code == 200
    data = response.json()
    
    # Check response structure
    assert "status" in data
    assert "metrics" in data
    assert "plots" in data
    
    # Check if metrics were calculated
    metrics = data["metrics"]
    assert "accuracy" in metrics
    assert "precision" in metrics
    assert "recall" in metrics
    assert "f1" in metrics
    assert "roc_auc" in metrics
    assert "avg_precision" in metrics