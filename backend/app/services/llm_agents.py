# Enhanced llm_agents.py with interactive consumer and producer decisions

import asyncio
import random
import os
from typing import Any, Dict, List, Optional

# ... (keep existing LLM setup code as is) ...

# Lazy-init GPT4All model
llm = None
_llm_failed = False

def _llm_disabled_env() -> bool:
    return os.environ.get("NEGOTIATION_HEURISTIC") == "1" or os.environ.get("GPT4ALL_DISABLE") == "1"

def get_llm():
    global llm, _llm_failed
    if _llm_disabled_env() or _llm_failed:
        raise RuntimeError("LLM disabled by env or previous failure")
    if llm is not None:
        return llm

    try:
        from gpt4all import GPT4All
    except Exception as e:
        _llm_failed = True
        raise RuntimeError(f"Failed to import GPT4All backend: {e}")

    model_name = os.environ.get("GPT4ALL_MODEL")
    try:
        if not model_name:
            available = GPT4All.list_models()
            if not available:
                raise RuntimeError("No GPT4All models found.")
            first = available[0]
            model_name = first["filename"] if isinstance(first, dict) and "filename" in first else str(first)
        llm = GPT4All(model_name)
        return llm
    except Exception as e:
        _llm_failed = True
        raise RuntimeError(f"Failed to initialize GPT4All model '{model_name}': {e}")

def _heuristic_offer(producer_id: int, product: Dict[str, Any], consumer_request: Dict[str, Any], round_num: int) -> Dict[str, Any]:
    base_price = float(product.get("price", 0))
    max_discount = 0.1 * base_price
    round_discount = (round_num / 10.0) * max_discount
    price = max(0.0, round(base_price - random.uniform(0, round_discount), 2))

    requested_qty = int(consumer_request.get("quantity", 0))
    available_qty = int(product.get("quantity", 0))
    quantity = max(0, min(available_qty, int(max(1, requested_qty) * random.uniform(0.8, 1.2))))

    # Add quality and reliability scores for satisfaction calculation
    quality_score = random.uniform(7.0, 9.5)  # Out of 10
    delivery_reliability = random.uniform(85, 98)  # Percentage
    payment_flexibility = random.uniform(6.0, 9.0)  # Out of 10

    return {
        "producer_id": producer_id,
        "producer_name": f"Producer #{producer_id}",
        "round": round_num,
        "offer": {
            "price": price,
            "quantity": quantity,
            "total_cost": round(price * quantity, 2),
            "note": f"Competitive offer from Producer #{producer_id}",
            "delivery_terms": f"{random.randint(7, 21)} days delivery",
            "payment_terms": random.choice(["30 days", "15 days", "Cash on delivery"]),
            "quality_rating": round(quality_score, 1),
            "delivery_reliability": round(delivery_reliability, 1),
            "payment_flexibility": round(payment_flexibility, 1)
        }
    }

# Enhanced producer agent
async def producer_agent(producer_id: int, product, consumer_request, round_num: int, use_llm: bool = True):
    """Enhanced producer that makes detailed offers."""
    if not use_llm or _llm_disabled_env() or _llm_failed:
        return _heuristic_offer(producer_id, product, consumer_request, round_num)

    prompt = f"""
    You are Producer #{producer_id} in round {round_num} of negotiation.
    Your Product: {product['name']} | Your Price: {product['price']} | Available: {product['quantity']} | Specs: {product['specs']}
    Consumer wants: {consumer_request}

    Make a competitive offer including:
    - Price per unit
    - Quantity you can supply
    - Delivery terms
    - Payment terms
    
    Be strategic - lower prices in later rounds but maintain profitability.
    """
    try:
        llm_inst = get_llm()
        with llm_inst.chat_session():
            response = llm_inst.generate(prompt, max_tokens=150)
        return {
            "producer_id": producer_id,
            "producer_name": f"Producer #{producer_id}",
            "round": round_num,
            "offer": response,
        }
    except Exception:
        return _heuristic_offer(producer_id, product, consumer_request, round_num)

def calculate_satisfaction_score(offer: Dict[str, Any], consumer_request: Dict[str, Any]) -> Dict[str, Any]:
    """Calculate consumer satisfaction percentage for an offer."""
    offer_details = offer.get("offer", {})
    
    # Extract values
    offered_price = float(offer_details.get("price", 0))
    consumer_budget = float(consumer_request.get("budget", 0))
    offered_qty = int(offer_details.get("quantity", 0))
    requested_qty = int(consumer_request.get("quantity", 0))
    total_cost = float(offer_details.get("total_cost", 0))
    
    # Quality metrics (from offer or defaults)
    quality_rating = float(offer_details.get("quality_rating", 8.0))
    delivery_reliability = float(offer_details.get("delivery_reliability", 90.0))
    payment_flexibility = float(offer_details.get("payment_flexibility", 7.0))
    
    # Calculate component scores (0-100 scale)
    
    # 1. Price Satisfaction (40% weight) - Lower price = higher satisfaction
    if consumer_budget > 0:
        price_satisfaction = max(0, min(100, ((consumer_budget - offered_price) / consumer_budget) * 100 + 50))
    else:
        price_satisfaction = 50
    
    # 2. Quantity Satisfaction (25% weight) - Closer to requested = higher satisfaction
    if requested_qty > 0:
        qty_ratio = min(offered_qty / requested_qty, 1.0)
        quantity_satisfaction = qty_ratio * 100
    else:
        quantity_satisfaction = 100
    
    # 3. Quality Satisfaction (15% weight) - Direct mapping from rating
    quality_satisfaction = (quality_rating / 10.0) * 100
    
    # 4. Delivery Satisfaction (10% weight) - Direct mapping from reliability
    delivery_satisfaction = delivery_reliability
    
    # 5. Payment Satisfaction (10% weight) - Direct mapping from flexibility
    payment_satisfaction = (payment_flexibility / 10.0) * 100
    
    # Calculate weighted total satisfaction
    total_satisfaction = (
        price_satisfaction * 0.40 +
        quantity_satisfaction * 0.25 +
        quality_satisfaction * 0.15 +
        delivery_satisfaction * 0.10 +
        payment_satisfaction * 0.10
    )
    
    # Determine satisfaction category
    if total_satisfaction >= 90:
        category = "Excellent"
        emoji = "🌟"
    elif total_satisfaction >= 80:
        category = "Very Good"
        emoji = "✅"
    elif total_satisfaction >= 70:
        category = "Good"
        emoji = "👍"
    elif total_satisfaction >= 50:
        category = "Fair"
        emoji = "⚠️"
    else:
        category = "Poor"
        emoji = "❌"
    
    return {
        "total_satisfaction": round(total_satisfaction, 1),
        "category": category,
        "emoji": emoji,
        "breakdown": {
            "price_satisfaction": round(price_satisfaction, 1),
            "quantity_satisfaction": round(quantity_satisfaction, 1), 
            "quality_satisfaction": round(quality_satisfaction, 1),
            "delivery_satisfaction": round(delivery_satisfaction, 1),
            "payment_satisfaction": round(payment_satisfaction, 1)
        },
        "strengths": [],
        "concerns": []
    }

def generate_recommendation(offers_with_satisfaction: List[Dict[str, Any]], consumer_request: Dict[str, Any]) -> Dict[str, Any]:
    """Generate AI-powered recommendation for the consumer."""
    
    if not offers_with_satisfaction:
        return {"recommendation": "No offers to evaluate", "reason": "No offers received"}
    
    budget = float(consumer_request.get("budget", 0))

    # Apply hard budget cap: only consider offers with price <= budget
    eligible = []
    for item in offers_with_satisfaction:
        details = item.get("offer", {})
        price = float(details.get("price", float("inf")))
        if budget and price > budget:
            continue
        eligible.append(item)

    if not eligible:
        return {
            "recommendation": "CONSIDER ALTERNATIVES",
            "confidence": "Low",
            "satisfaction_score": 0,
            "reason": "All offers exceed budget",
            "recommended_producer": None,
            "recommended_producer_id": None,
            "strengths": [],
            "risk_factors": ["budget cap exceeded"] ,
            "alternative_consideration": False
        }

    # Sort by satisfaction desc; if within 3% satisfaction, prefer lower price
    def sort_key(item: Dict[str, Any]):
        sat = float(item["satisfaction"]["total_satisfaction"]) if item.get("satisfaction") else 0.0
        price = float(item.get("offer", {}).get("price", float("inf")))
        return (-sat, price)

    eligible_sorted = sorted(eligible, key=sort_key)

    best_offer = eligible_sorted[0]
    best_satisfaction = best_offer["satisfaction"]["total_satisfaction"]

    # Build reasons and risk factors as before
    recommendation_reasons = []
    breakdown = best_offer["satisfaction"]["breakdown"]
    if breakdown["price_satisfaction"] >= 80:
        recommendation_reasons.append("excellent price value")
    if breakdown["quantity_satisfaction"] >= 90:
        recommendation_reasons.append("meets quantity requirements perfectly")
    if breakdown["quality_satisfaction"] >= 85:
        recommendation_reasons.append("high quality rating")
    if breakdown["delivery_satisfaction"] >= 95:
        recommendation_reasons.append("reliable delivery track record")

    risk_factors = []
    if breakdown["price_satisfaction"] < 40:
        risk_factors.append("price exceeds budget significantly")
    if breakdown["quantity_satisfaction"] < 70:
        risk_factors.append("quantity shortfall")
    if breakdown["delivery_satisfaction"] < 80:
        risk_factors.append("delivery reliability concerns")

    producer_name = best_offer.get("producer_name", "Unknown Producer")

    if best_satisfaction >= 90:
        recommendation = f"HIGHLY RECOMMENDED: {producer_name}"
        confidence = "High"
    elif best_satisfaction >= 80:
        recommendation = f"RECOMMENDED: {producer_name}"
        confidence = "Medium"
    elif best_satisfaction >= 70:
        recommendation = f"ACCEPTABLE: {producer_name}"
        confidence = "Medium"
    else:
        recommendation = f"CONSIDER ALTERNATIVES: {producer_name}"
        confidence = "Low"

    reason_text = f"{producer_name} scored {best_satisfaction}% satisfaction"
    if recommendation_reasons:
        reason_text += f" due to {', '.join(recommendation_reasons[:2])}"

    return {
        "recommended_producer": producer_name,
        "recommended_producer_id": best_offer["producer_id"],
        "recommendation": recommendation,
        "confidence": confidence,
        "satisfaction_score": best_satisfaction,
        "reason": reason_text,
        "strengths": recommendation_reasons,
        "risk_factors": risk_factors,
        "alternative_consideration": len(eligible_sorted) > 1 and eligible_sorted[1]["satisfaction"]["total_satisfaction"] > 70
    }

def display_offers_to_consumer(offers: List[Dict[str, Any]], consumer_request: Dict[str, Any], round_num: int) -> List[Dict[str, Any]]:
    """Display offers with satisfaction analysis and a recommendation.
    Returns only budget-eligible offers for selection.
    """
    print(f"\n{'='*60}")
    print(f"ROUND {round_num} - PRODUCER OFFERS")
    print(f"{'='*60}")

    offers_with_scores: List[Dict[str, Any]] = []
    eligible_offers: List[Dict[str, Any]] = []
    rejected_over_budget: List[Dict[str, Any]] = []

    budget = float(consumer_request.get("budget", 0))

    # Display eligible offers first
    option_index = 1
    for offer in offers:
        producer_name = offer.get("producer_name", f"Producer #{offer['producer_id']}")
        offer_details = offer.get("offer", {})
        satisfaction = calculate_satisfaction_score(offer, consumer_request)
        price = float(offer_details.get("price", float("inf")))
        enriched = {**offer, "satisfaction": satisfaction}

        if budget and price > budget:
            rejected_over_budget.append(enriched)
            continue

        print(f"\nOption {option_index}: {producer_name} {satisfaction['emoji']}")
        print(f"  Price: ${offer_details.get('price', 'N/A')} per unit")
        print(f"  Quantity: {offer_details.get('quantity', 'N/A')} units")
        print(f"  Total Cost: ${offer_details.get('total_cost', 'N/A')}")
        print(f"  Delivery: {offer_details.get('delivery_terms', 'Standard')}")
        print(f"  Payment: {offer_details.get('payment_terms', 'Standard')}")
        if isinstance(offer_details, str):
            preview = offer_details.replace('\n', ' ')[:100]
            print(f"  Details: {preview}...")
        elif offer_details.get('note'):
            print(f"  Note: {offer_details['note']}")
        print(f"  Satisfaction: {satisfaction['total_satisfaction']}% ({satisfaction['category']})")

        offers_with_scores.append(enriched)
        eligible_offers.append(enriched)
        option_index += 1

    # Show over-budget offers as rejected
    if rejected_over_budget:
        print(f"\n-- Rejected (over budget) --")
        for item in rejected_over_budget:
            details = item.get("offer", {})
            print(f"  {item.get('producer_name', 'Producer')} | Price: ${details.get('price', 'N/A')} > Budget ${budget}")

    # Show AI recommendation summary based on eligible only
    try:
        recommendation = generate_recommendation(eligible_offers, consumer_request)
        print(f"\nAI Recommendation: {recommendation.get('recommendation')} ({recommendation.get('confidence', 'N/A')} confidence)")
        print(f"Reason: {recommendation.get('reason')}")
    except Exception:
        pass

    return eligible_offers

def get_consumer_choice(offers: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    """Get consumer's manual choice of offer."""
    while True:
        try:
            print(f"\nEnter your choice (1-{len(offers)}) or 0 to decline all offers:")
            choice = int(input("Your choice: "))
            
            if choice == 0:
                print("You declined all offers for this round.")
                return None
            elif 1 <= choice <= len(offers):
                selected = offers[choice - 1]
                print(f"You selected {selected.get('producer_name', 'Unknown Producer')}'s offer.")
                return selected
            else:
                print(f"Please enter a number between 0 and {len(offers)}")
        except ValueError:
            print("Please enter a valid number.")

def get_producer_response(offer: Dict[str, Any], round_num: int) -> Dict[str, Any]:
    """Simulate producer's decision to accept/decline consumer's choice."""
    producer_name = offer.get("producer_name", f"Producer #{offer['producer_id']}")
    offer_details = offer.get("offer", {})
    
    print(f"\n{producer_name} is considering your acceptance...")
    
    # Heuristic: producers are more likely to accept in later rounds
    acceptance_probability = 0.7 + (round_num * 0.1)  # 70% + 10% per round
    
    if random.random() < acceptance_probability:
        print(f"✅ {producer_name} ACCEPTS the deal!")
        return {
            "producer_response": "accepted",
            "producer_name": producer_name,
            "final_terms": offer_details,
            "message": f"{producer_name} is happy to proceed with this deal."
        }
    else:
        print(f"❌ {producer_name} DECLINES the deal.")
        reasons = [
            "Price is too low for our quality standards",
            "Cannot meet the delivery timeline",
            "Minimum quantity requirements not met",
            "Market conditions have changed"
        ]
        return {
            "producer_response": "declined",
            "producer_name": producer_name,
            "reason": random.choice(reasons),
            "message": f"{producer_name} cannot accept this deal at this time."
        }

def get_final_consumer_decision(accepted_deals: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    """Let consumer make final decision from accepted deals."""
    if not accepted_deals:
        print("\n❌ No producers accepted your choices. Negotiation failed.")
        return None
    
    print(f"\n{'='*60}")
    print("FINAL DECISION - CHOOSE YOUR PREFERRED DEAL")
    print(f"{'='*60}")
    
    print(f"\nYou have {len(accepted_deals)} accepted offer(s):")
    for i, deal in enumerate(accepted_deals, 1):
        producer_name = deal.get("producer_name", "Unknown")
        terms = deal.get("final_terms", {})
        print(f"\n{i}. {producer_name}")
        print(f"   Price: ${terms.get('price', 'N/A')} per unit")
        print(f"   Quantity: {terms.get('quantity', 'N/A')} units")
        print(f"   Total: ${terms.get('total_cost', 'N/A')}")
        print(f"   Message: {deal.get('message', 'Ready to proceed')}")
    
    while True:
        try:
            choice = int(input(f"\nFinal choice (1-{len(accepted_deals)}) or 0 to cancel: "))
            if choice == 0:
                print("❌ You cancelled the negotiation.")
                return None
            elif 1 <= choice <= len(accepted_deals):
                final_deal = accepted_deals[choice - 1]
                print(f"🎉 Deal finalized with {final_deal['producer_name']}!")
                return final_deal
            else:
                print(f"Please enter a number between 0 and {len(accepted_deals)}")
        except ValueError:
            print("Please enter a valid number.")

# Enhanced orchestrator with interactive consumer decisions
async def negotiate_multi_round_interactive(product, consumer_request, num_producers=3, num_rounds=3, use_llm: bool = True, producer_id_pool: int = 3, interactive: bool = True):
    """Interactive multi-round negotiation where consumer manually chooses offers."""
    history = []
    consumer_choices = []
    
    if interactive:
        print(f"\n🏪 Starting negotiation for {consumer_request['product_name']}")
        print(f"Requested: {consumer_request['quantity']} units, Budget: ${consumer_request['budget']}")
    
    # Multi-round offer generation and consumer selection
    for round_num in range(1, num_rounds + 1):
        if interactive:
            print(f"\n🔄 Generating offers for Round {round_num}...")
        
        # Get all producer offers in parallel
        # Sample unique producer IDs from a larger pool (e.g., 1..5) while keeping num_producers offers per round
        pool_size = max(num_producers, int(producer_id_pool) if producer_id_pool else num_producers)
        available_ids = list(range(1, pool_size + 1))
        try:
            selected_ids = random.sample(available_ids, k=num_producers)
        except ValueError:
            # Fallback if pool smaller than requested num_producers
            selected_ids = available_ids[:num_producers]

        tasks = [
            producer_agent(pid, product, consumer_request, round_num, use_llm=use_llm)
            for pid in selected_ids
        ]
        round_offers = await asyncio.gather(*tasks)
        
        # Display or just compute eligible offers depending on mode
        if interactive:
            eligible_offers = display_offers_to_consumer(round_offers, consumer_request, round_num)
            # Get consumer's choice from eligible offers only
            if not eligible_offers:
                print("\nNo eligible offers within budget this round.")
                consumer_choice = None
            else:
                consumer_choice = get_consumer_choice(eligible_offers)
        else:
            # In non-interactive mode, compute eligibility but do not prompt
            eligible_offers = display_offers_to_consumer(round_offers, consumer_request, round_num)
            consumer_choice = None
        
        # Store round result
        round_result = {
            "round": round_num,
            "offers": round_offers,
            "eligible_offers": eligible_offers,
            "consumer_choice": consumer_choice,
            "producer_response": None
        }
        
        if interactive and consumer_choice:
            # Get producer's response to consumer's choice
            producer_response = get_producer_response(consumer_choice, round_num)
            round_result["producer_response"] = producer_response
            consumer_choices.append({
                "round": round_num,
                "choice": consumer_choice,
                "producer_response": producer_response
            })
        
        history.append(round_result)
    
    # Final decision phase - consumer chooses from accepted deals
    accepted_deals = [
        choice["producer_response"] 
        for choice in consumer_choices 
        if choice["producer_response"]["producer_response"] == "accepted"
    ]
    
    final_deal = get_final_consumer_decision(accepted_deals) if interactive else None
    
    return {
        "negotiation_history": history,
        "consumer_choices": consumer_choices,
        "final_deal": final_deal,
        "negotiation_status": "completed" if final_deal else "in_progress"
    }

# Backward compatibility - keep original function
async def negotiate_multi_round(product, consumer_request, num_producers=3, num_rounds=3, use_llm: bool = True):
    """Original automated negotiation function."""
    return await negotiate_multi_round_interactive(product, consumer_request, num_producers, num_rounds, use_llm)