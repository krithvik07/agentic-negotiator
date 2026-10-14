# scripts/test_interactive_negotiation.py

import sys
import os
import json
import asyncio

# Add project root to sys.path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

# Import the enhanced negotiation orchestrator
from backend.app.services.llm_agents import negotiate_multi_round_interactive

# Domain scenarios aligned to DB-like ranges (price: 20–100, quantity: 100–1000)
DOMAINS = {
    "agriculture": {
        "product": {
            "name": "Wheat",
            "price": 55.0,
            "quantity": 800,
            "specs": {"quality": "A", "origin": "Punjab"}
        },
        "consumer_request": {
            "product_name": "Wheat",
            "quantity": 300,
            "budget": 60.0,
            "specs": {"quality": "A"}
        }
    },
    "construction": {
        "product": {
            "name": "Cement",
            "price": 70.0,
            "quantity": 900,
            "specs": {"quality": "A", "origin": "Gujarat"}
        },
        "consumer_request": {
            "product_name": "Cement",
            "quantity": 500,
            "budget": 75.0,
            "specs": {"quality": "A"}
        }
    },
    "handicrafts": {
        "product": {
            "name": "Handmade Pottery",
            "price": 45.0,
            "quantity": 300,
            "specs": {"quality": "A", "origin": "Jaipur"}
        },
        "consumer_request": {
            "product_name": "Handmade Pottery",
            "quantity": 150,
            "budget": 50.0,
            "specs": {"quality": "A"}
        }
    },
    "pharmaceuticals": {
        "product": {
            "name": "Paracetamol Tablets",
            "price": 35.0,
            "quantity": 1000,
            "specs": {"quality": "A", "origin": "Hyderabad"}
        },
        "consumer_request": {
            "product_name": "Paracetamol Tablets",
            "quantity": 400,
            "budget": 40.0,
            "specs": {"quality": "A"}
        }
    },
    "textiles": {
        "product": {
            "name": "Cotton Fabric",
            "price": 60.0,
            "quantity": 700,
            "specs": {"quality": "A", "origin": "Tiruppur"}
        },
        "consumer_request": {
            "product_name": "Cotton Fabric",
            "quantity": 350,
            "budget": 65.0,
            "specs": {"quality": "A"}
        }
    }
}

# Helper to choose a domain scenario
def choose_domain_scenario():
    options = list(DOMAINS.keys())
    print("Select a domain:")
    for i, key in enumerate(options, 1):
        print(f"  {i}. {key}")
    try:
        sel = int(input(f"Enter choice (1-{len(options)}) [default 1]: ") or 1)
        if not (1 <= sel <= len(options)):
            sel = 1
    except ValueError:
        sel = 1
    domain = options[sel - 1]
    scenario = DOMAINS[domain]
    return domain, scenario["product"], scenario["consumer_request"]

# Default sample product and consumer request (will be overridden by selection)
product = {
    "name": "Wheat",  # align with DB product names list
    "price": 55.0,
    "quantity": 800,
    "specs": {"quality": "A", "origin": "Punjab"}  # align with DB quality grades
}

consumer_request = {
    "product_name": "Wheat",  # align with DB product names
    "quantity": 300,  # within DB range [100, 1000]
    "budget": 60.0,   # within DB range [20.0, 100.0]
    "specs": {"quality": "A"}  # align with DB quality grades {A, B, C}
}

async def main():
    print("🤝 MULTI-DOMAIN NEGOTIATION SYSTEM")
    print("=" * 50)

    # Domain selection
    domain, prod, req = choose_domain_scenario()
    print(f"\nDomain selected: {domain}")

    # Override defaults with chosen scenario
    global product, consumer_request
    product = prod
    consumer_request = req

    # Run interactive negotiation
    use_llm = False  # Set to True for LLM-powered agents

    result = await negotiate_multi_round_interactive(
        product,
        consumer_request,
        num_producers=3,  # Show 3 producers
        num_rounds=3,     # 3 rounds of negotiation
        use_llm=use_llm,
    )

    # Display final results
    print(f"\n{'='*60}")
    print("NEGOTIATION SUMMARY")
    print(f"{'='*60}")

    if result["final_deal"]:
        deal = result["final_deal"]
        terms = deal.get("final_terms", {})
        print(f"✅ SUCCESS! Deal completed with {deal['producer_name']}")
        print(f"   Final Price: ${terms.get('price', 'N/A')} per unit")
        print(f"   Quantity: {terms.get('quantity', 'N/A')} units")
        print(f"   Total Cost: ${terms.get('total_cost', 'N/A')}")
        print(f"   Delivery: {terms.get('delivery_terms', 'Standard')}")
        print(f"   Payment: {terms.get('payment_terms', 'Standard')}")
    else:
        print("❌ NEGOTIATION FAILED - No deal was reached")

    print(f"\nNegotiation Status: {result['negotiation_status'].upper()}")

    # Optionally save detailed results
    with open("negotiation_results.json", "w") as f:
        json.dump(result, f, indent=2)
    print(f"\nDetailed results saved to: negotiation_results.json")

if __name__ == "__main__":
    asyncio.run(main())