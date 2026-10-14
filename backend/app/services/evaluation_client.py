import requests
from typing import Dict, Any, Optional
import json
from pathlib import Path

class EvaluationClient:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url.rstrip('/')
    
    def record_outcome(self, 
                      session_id: str, 
                      accepted: bool, 
                      predicted_prob: float,
                      features: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Record the outcome of a negotiation."""
        url = f"{self.base_url}/negotiation/record-outcome"
        payload = {
            "session_id": session_id,
            "accepted": accepted,
            "predicted_prob": predicted_prob,
            "features": features or {}
        }
        response = requests.post(url, json=payload)
        response.raise_for_status()
        return response.json()
    
    def generate_report(self, save_dir: str = "reports/figures") -> Dict[str, Any]:
        """Generate and save performance report."""
        url = f"{self.base_url}/evaluation/report"
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        
        # Ensure the save directory exists
        Path(save_dir).mkdir(parents=True, exist_ok=True)
        
        # Save metrics
        metrics_path = Path(save_dir) / "metrics.json"
        with open(metrics_path, 'w') as f:
            json.dump(data["metrics"], f, indent=2)
        
        return data

# Example usage
if __name__ == "__main__":
    client = EvaluationClient()
    
    # Example: Record an outcome
    try:
        result = client.record_outcome(
            session_id="test-session-123",
            accepted=True,
            predicted_prob=0.85,
            features={
                "initial_price": 1000,
                "final_price": 900,
                "rounds": 3
            }
        )
        print("Outcome recorded:", result)
        
        # Generate and save report
        report = client.generate_report()
        print("Report generated at:", report["plots"])
        
    except Exception as e:
        print(f"Error: {e}")