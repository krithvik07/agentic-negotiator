import requests
import json

url = "http://127.0.0.1:8000/api/negotiations/record-outcome"

# Sample data for the negotiation outcome
data = {
    "session_id": "test-session-1",
    "accepted": True,
    "predicted_prob": 0.85,
    "features": {
        "rounds": 3,
        "final_price": 150.0,
        "initial_price": 200.0
    }
}

try:
    response = requests.post(url, json=data)
    response.raise_for_status()  # Raise an error for bad status codes
    print("Successfully recorded outcome:")
    print(json.dumps(response.json(), indent=2))
except requests.exceptions.RequestException as e:
    print(f"Error recording outcome: {e}")