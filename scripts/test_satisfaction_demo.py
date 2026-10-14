# scripts/test_satisfaction_demo.py

import sys
import os
import json
import asyncio

# Add project root to sys.path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

# Import the enhanced negotiation orchestrator
from backend.app.services.llm_agents import negotiate_multi_round_interactive

# Sample realistic scenarios for testing satisfaction scoring
scenarios = [
    {
        "name": "High Budget Consumer (Premium Wheat)",
        "product": {
            "name": "Premium Organic Wheat",
            "price": 45.0,
            "quantity": 1000,
            "specs": {"quality": "Grade A+", "organic": True, "origin": "Punjab"}
        },
        "consumer_request": {
            "product_name": "Premium Organic Wheat",
            "quantity": 300,
            "budget": 55.0,  # Higher budget - should get better satisfaction
            "specs": {"quality": "Grade A+", "organic": True}
        }
    },
    {
        "name": "Budget-Conscious Consumer (Standard Wheat)",
        "product": {
            "name": "Standard Wheat",
            "price": 35.0,
            "quantity": 800,
            "specs": {"quality": "Grade B", "organic": False, "origin": "Rajasthan"}
        },
        "consumer_request": {
            "product_name": "Standard Wheat",
            "quantity": 500,
            "budget": 30.0,  # Lower budget - challenging satisfaction
            "specs": {"quality": "Grade B"}
        }
    },
    {
        "name": "Large Order Consumer (Bulk Rice)",
        "product": {
            "name": "Basmati Rice",
            "price": 65.0,
            "quantity": 2000,
            "specs": {"quality": "Grade A", "variety": "1121", "origin": "Haryana"}
        },
        "consumer_request": {
            "product_name": "Basmati Rice",
            "quantity": 1500,  # Large quantity request
            "budget": 70.0,
            "specs": {"quality": "Grade A", "variety": "1121"}
        }
    }
]

async def run_satisfaction_demo():
    print("🎯 SATISFACTION SCORING SYSTEM DEMO")
    print("=" * 60)
    print("This demo shows how the AI evaluates offers and provides recommendations")
    print("based on consumer satisfaction scores across multiple criteria.\n")
    
    for i, scenario in enumerate(scenarios, 1):
        print(f"\n{'🔸' * 20} SCENARIO {i}: {scenario['name']} {'🔸' * 20}")
        
        # Show scenario details
        print(f"\n📋 SCENARIO DETAILS:")
        consumer_req = scenario['consumer_request']
        print(f"   Product Needed: {consumer_req['product_name']}")
        print(f"   Quantity Needed: {consumer_req['quantity']} units")
        print(f"   Budget: ${consumer_req['budget']} per unit")
        print(f"   Requirements: {consumer_req['specs']}")
        
        # Run one round of negotiation to see satisfaction scoring
        result = await negotiate_multi_round_interactive(
            scenario["product"],
            scenario["consumer_request"],
            num_producers=3,
            num_rounds=1,  # Just one round for demo
            use_llm=False  # Use heuristic for consistent demo
        )
        
        # Extract and display results
        if result["negotiation_history"]:
            round_data = result["negotiation_history"][0]
            
            print(f"\n📊 SATISFACTION ANALYSIS RESULTS:")
            print(f"   Number of offers received: {len(round_data['offers'])}")
            
            # This would normally be shown in the interactive display
            # For demo, we'll show a summary
            print(f"   🤖 AI provided satisfaction scores and recommendations")
            print(f"   📈 Consumer can compare all options with detailed breakdowns")
            print(f"   ✨ System highlights the most satisfactory choice")
        
        # Ask if user wants to see detailed results
        show_details = input(f"\nWould you like to see the detailed results for this scenario? (y/n): ").lower()
        if show_details == 'y':
            print("\n" + "="*80)
            print("DETAILED RESULTS:")
            print("="*80)
            print(json.dumps(result, indent=2))
        
        if i < len(scenarios):
            input("\nPress Enter to continue to next scenario...")

async def run_single_interactive_demo():
    """Run one interactive negotiation using one of the predefined scenarios."""
    print("🌾 SINGLE INTERACTIVE NEGOTIATION DEMO")
    print("=" * 60)

    # Let user choose a scenario
    print("Select a scenario to run:")
    for idx, sc in enumerate(scenarios, 1):
        print(f"  {idx}. {sc['name']}")

    try:
        choice = int(input(f"Enter choice (1-{len(scenarios)}) [default 1]: ") or 1)
        if not (1 <= choice <= len(scenarios)):
            print("Invalid choice. Defaulting to 1.")
            choice = 1
    except ValueError:
        print("Invalid input. Defaulting to 1.")
        choice = 1

    scenario = scenarios[choice - 1]
    product = scenario["product"]
    consumer_request = scenario["consumer_request"]

    print(f"\nRunning: {scenario['name']}")
    print(f"Product: {product['name']} | Price: ${product['price']} | Stock: {product['quantity']}")
    print(f"Consumer Needs: {consumer_request['quantity']} units | Budget: ${consumer_request['budget']}\n")

    # Run negotiation interactively (multi-round)
    result = await negotiate_multi_round_interactive(
        product,
        consumer_request,
        num_producers=3,
        num_rounds=3,
        use_llm=False,
    )

    print(f"\n{'='*60}")
    print("NEGOTIATION RESULT")
    print(f"{'='*60}")
    if result.get("final_deal"):
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
    print(f"\nNegotiation Status: {result.get('negotiation_status', 'unknown').upper()}")

if __name__ == "__main__":
    # Offer a simple menu to run either the satisfaction demo or a single interactive run
    print("Select mode:")
    print("  1. Satisfaction Scoring Demo (non-interactive summary per scenario)")
    print("  2. Single Interactive Negotiation (step-by-step choices)")
    try:
        mode = int(input("Enter choice (1-2) [default 1]: ") or 1)
    except ValueError:
        mode = 1

    if mode == 2:
        asyncio.run(run_single_interactive_demo())
    else:
        asyncio.run(run_satisfaction_demo())