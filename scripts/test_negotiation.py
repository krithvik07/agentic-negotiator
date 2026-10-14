# scripts/test_negotiation.py

import sys
import os
import json
import asyncio

# -----------------------------
# Fix import path for backend
# -----------------------------
# Add project root to sys.path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

# Import the negotiation orchestrator (async)
from backend.app.services.llm_agents import negotiate_multi_round

# -----------------------------
# Sample product and consumer request
# -----------------------------
product = {
    "name": "Wheat",
    "price": 50.0,
    "quantity": 500,
    "specs": {"quality": "A"}
}

consumer_request = {
    "product_name": "Wheat",
    "quantity": 200,
    "budget": 55.0,
    "specs": {"quality": "A"}
}

async def main():
    # Force fast heuristic mode for this test run
    use_llm = False

    history = await negotiate_multi_round(
        product,
        consumer_request,
        num_producers=2,  # reduce for speed during tests
        num_rounds=1,     # reduce for speed during tests
        use_llm=use_llm,
    )
    print("Negotiation History:")
    print(json.dumps(history, indent=4))

if __name__ == "__main__":
    asyncio.run(main())
