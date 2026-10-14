# Enhanced main.py with interactive negotiation support

from .services.evaluation_client import EvaluationClient
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, Any
from .services.llm_agents import negotiate_multi_round_interactive, calculate_satisfaction_score, generate_recommendation, get_producer_response
from fastapi.staticfiles import StaticFiles


app = FastAPI(title="Enhanced Negotiation API", version="2.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Mount modular routers
from .routes.auth import router as auth_router
from backend.app.routes.products import router as products_router
from backend.app.routes.requests import router as requests_router

app.include_router(auth_router, prefix="/auth", tags=["auth"])
app.include_router(products_router, prefix="/products", tags=["products"])
app.include_router(requests_router, prefix="/requests", tags=["requests"])

# --- Enhanced Schemas ---
class Product(BaseModel):
    name: str
    price: float
    quantity: int
    specs: Optional[Dict[str, Any]] = None

class ConsumerRequest(BaseModel):
    product_name: str
    quantity: int
    budget: float
    specs: Optional[Dict[str, Any]] = None

class NegotiationConfig(BaseModel):
    product: Product
    consumer_request: ConsumerRequest
    num_producers: int = 3
    num_rounds: int = 3
    use_llm: bool = False

class ChoosePayload(BaseModel):
    round_number: int
    offer_index: int

class ConsumerChoice(BaseModel):
    round_number: int
    chosen_producer_id: Optional[int] = None  # None means declined all offers

class FinalDecision(BaseModel):
    chosen_deal_index: Optional[int] = None  # None means cancelled negotiation

# --- In-memory storage for demo (use Redis/DB in production) ---
negotiations = {}  # session_id -> negotiation_data

# --- Routes ---
@app.get("/")
def root_redirect():
    return RedirectResponse(url="/frontend/")

@app.post("/negotiation/start")
async def start_negotiation(config: NegotiationConfig):
    """Start a new negotiation session and return offers for first round."""
    try:
        # Generate session ID
        import uuid
        session_id = str(uuid.uuid4())
        
        # Run negotiation to get all offers
        result = await negotiate_multi_round_interactive(
            config.product.dict(),
            config.consumer_request.dict(),
            num_producers=config.num_producers,
            num_rounds=config.num_rounds,
            use_llm=config.use_llm,
            interactive=False,
        )
        
        # Store session data
        negotiations[session_id] = {
            "config": config.dict(),
            "result": result,
            "current_round": 1,
            "status": "in_progress"
        }
        
        # Return first round offers with satisfaction analysis
        first_round = result["negotiation_history"][0] if result["negotiation_history"] else None
        
        if first_round:
            # Add satisfaction scores to first round offers
            offers_with_satisfaction = []
            for offer in first_round["eligible_offers"] or first_round["offers"]:
                satisfaction = calculate_satisfaction_score(offer, config.consumer_request.dict()) if "satisfaction" not in offer else offer["satisfaction"]
                offer_with_sat = {
                    **offer,
                    "satisfaction_score": satisfaction["total_satisfaction"] if isinstance(satisfaction, dict) else satisfaction,
                    "satisfaction_category": satisfaction["category"] if isinstance(satisfaction, dict) else None,
                    "satisfaction_breakdown": satisfaction["breakdown"] if isinstance(satisfaction, dict) else None,
                    "satisfaction_emoji": satisfaction.get("emoji") if isinstance(satisfaction, dict) else None
                }
                offers_with_satisfaction.append(offer_with_sat)
            
            # Generate AI recommendation
            recommendation = generate_recommendation(
                [{"satisfaction": calculate_satisfaction_score(offer, config.consumer_request.dict()), **offer} 
                 for offer in first_round["eligible_offers"] or first_round["offers"]], 
                config.consumer_request.dict()
            )
        else:
            offers_with_satisfaction = []
            recommendation = {"recommendation": "No offers available", "reason": "No offers generated"}
        
        return {
            "session_id": session_id,
            "round": 1,
            "offers": offers_with_satisfaction,
            "ai_recommendation": recommendation,
            "total_rounds": config.num_rounds,
            "message": "Negotiation started. Review satisfaction scores and AI recommendation before choosing.",
            "status": negotiations[session_id]["status"]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/negotiation/{session_id}/round/{round_number}")
def get_round_offers(session_id: str, round_number: int):
    """Get offers for a specific round with satisfaction analysis."""
    if session_id not in negotiations:
        raise HTTPException(status_code=404, detail="Negotiation session not found")
    
    session_data = negotiations[session_id]
    history = session_data["result"]["negotiation_history"]
    consumer_request = session_data["config"]["consumer_request"]
    
    if round_number > len(history):
        raise HTTPException(status_code=404, detail="Round not found")
    
    round_data = history[round_number - 1]
    offers = round_data["offers"]
    
    # Calculate satisfaction scores for each offer
    offers_with_satisfaction = []
    for offer in offers:
        satisfaction = calculate_satisfaction_score(offer, consumer_request)
        offer_with_sat = {
            **offer,
            "satisfaction_score": satisfaction["total_satisfaction"],
            "satisfaction_category": satisfaction["category"],
            "satisfaction_breakdown": satisfaction["breakdown"],
            "satisfaction_emoji": satisfaction["emoji"]
        }
        offers_with_satisfaction.append(offer_with_sat)
    
    # Generate AI recommendation
    recommendation = generate_recommendation(
        [{"satisfaction": calculate_satisfaction_score(offer, consumer_request), **offer} 
         for offer in offers], 
        consumer_request
    )
    
    return {
        "session_id": session_id,
        "round": round_number,
        "offers": offers_with_satisfaction,
        "ai_recommendation": recommendation,
        "total_rounds": session_data["config"]["num_rounds"],
        "consumer_request": consumer_request
    }

@app.post("/negotiation/{session_id}/choose")
def make_consumer_choice(session_id: str, choice: ChoosePayload):
    """Consumer makes a choice for a specific round. Simulate producer response and advance state."""
    if session_id not in negotiations:
        raise HTTPException(status_code=404, detail="Negotiation session not found")
    
    session_data = negotiations[session_id]
    history = session_data["result"]["negotiation_history"]
    consumer_request = session_data["config"]["consumer_request"]
    round_number = choice.round_number
    idx = choice.offer_index - 1  # UI is 1-based
    
    if round_number < 1 or round_number > len(history):
        raise HTTPException(status_code=400, detail="Invalid round number")
    round_data = history[round_number - 1]
    eligible = round_data.get("eligible_offers") or round_data.get("offers")
    if not eligible:
        raise HTTPException(status_code=400, detail="No eligible offers in this round")
    if idx < 0 or idx >= len(eligible):
        raise HTTPException(status_code=400, detail="Invalid offer index")
    
    selected = eligible[idx]
    # Simulate producer response using existing helper
    producer_response = get_producer_response(selected, round_data["round"])  # synchronous helper
    
    # Attach to round and consumer_choices in result
    round_data["consumer_choice"] = selected
    round_data["producer_response"] = producer_response
    session_data["result"].setdefault("consumer_choices", []).append({
        "round": round_number,
        "choice": selected,
        "producer_response": producer_response
    })
    
    # If this was the last round, negotiation can be finalized by the client from accepted deals via /summary and /finalize
    negotiations[session_id] = session_data
    
    return {
        "session_id": session_id,
        "round": round_number,
        "selected_offer": selected,
        "producer_response": producer_response,
        "status": session_data.get("status", "in_progress")
    }

@app.get("/negotiation/{session_id}/summary")
def get_negotiation_summary(session_id: str):
    """Get complete negotiation summary."""
    if session_id not in negotiations:
        raise HTTPException(status_code=404, detail="Negotiation session not found")
    
    session_data = negotiations[session_id]
    result = session_data["result"]
    
    return {
        "session_id": session_id,
        "status": result["negotiation_status"],
        "final_deal": result.get("final_deal"),
        "total_rounds_completed": len(result["negotiation_history"]),
        "consumer_choices": result.get("consumer_choices", []),
        "negotiation_history": result["negotiation_history"]
    }

@app.post("/negotiation/{session_id}/finalize")
def finalize_negotiation(session_id: str, decision: FinalDecision):
    """Consumer makes final decision from accepted deals."""
    if session_id not in negotiations:
        raise HTTPException(status_code=404, detail="Negotiation session not found")
    
    session_data = negotiations[session_id]
    result = session_data["result"]
    
    # Get accepted deals
    accepted_deals = [
        choice["producer_response"] 
        for choice in result.get("consumer_choices", [])
        if choice.get("producer_response", {}).get("producer_response") == "accepted"
    ]
    
    if decision.chosen_deal_index is None:
        return {
            "session_id": session_id,
            "status": "cancelled",
            "message": "Negotiation cancelled by consumer"
        }
    
    if decision.chosen_deal_index >= len(accepted_deals):
        raise HTTPException(status_code=400, detail="Invalid deal selection")
    
    final_deal = accepted_deals[decision.chosen_deal_index]
    
    # Update session
    session_data["status"] = "completed"
    session_data["result"]["final_deal"] = final_deal
    
    return {
        "session_id": session_id,
        "status": "completed",
        "final_deal": final_deal,
        "message": f"Deal finalized with {final_deal['producer_name']}!"
    }

@app.delete("/negotiation/{session_id}")
def cancel_negotiation(session_id: str):
    """Cancel/delete a negotiation session."""
    if session_id not in negotiations:
        raise HTTPException(status_code=404, detail="Negotiation session not found")
    
    del negotiations[session_id]
    return {"message": "Negotiation session cancelled and deleted"}

@app.get("/negotiations/active")
def get_active_negotiations():
    """Get list of all active negotiation sessions."""
    return {
        "active_sessions": list(negotiations.keys()),
        "total_active": len(negotiations)
    }

# Mount a separate static frontend (create a 'frontend' folder at repo root)
app.mount("/frontend", StaticFiles(directory="frontend", html=True), name="frontend")



# Add to your imports
import numpy as np
from pathlib import Path
from typing import Dict, List, Optional
from fastapi import HTTPException
from .evaluation import generate_performance_report

# Add to your existing code
class NegotiationOutcome(BaseModel):
    session_id: str
    accepted: bool
    predicted_prob: float
    features: Optional[Dict[str, Any]] = None

# Add this global variable to store negotiation outcomes
negotiation_outcomes: List[Dict] = []

# Add this endpoint to record negotiation outcomes
@app.post("/negotiation/record-outcome", response_model=Dict[str, Any])
async def record_negotiation_outcome(outcome: NegotiationOutcome):
    """Record the outcome of a negotiation for evaluation."""
    if outcome.session_id not in negotiations:
        raise HTTPException(status_code=404, detail="Negotiation session not found")
    
    # Store the outcome
    negotiation_outcomes.append({
        'session_id': outcome.session_id,
        'accepted': outcome.accepted,
        'predicted_prob': outcome.predicted_prob,
        'features': outcome.features or {}
    })
    
    return {"status": "success", "message": "Outcome recorded"}

# Add this endpoint to generate performance report
@app.get("/api/evaluation/report", response_model=Dict[str, Any])
async def generate_evaluation_report():
    """Generate and return performance metrics and plots."""
    if not negotiation_outcomes:
        raise HTTPException(status_code=400, detail="No negotiation outcomes recorded yet")
    
    # Prepare data
    y_true = np.array([1 if o['accepted'] else 0 for o in negotiation_outcomes])
    y_scores = np.array([o['predicted_prob'] for o in negotiation_outcomes])
    
    # Generate report
    output_dir = "reports/figures"
    metrics = generate_performance_report(y_true, y_scores, output_dir)
    
    return {
        "status": "success",
        "metrics": metrics,
        "plots": {
            "confusion_matrix": f"{output_dir}/confusion_matrix.png",
            "roc_curve": f"{output_dir}/roc_curve.png",
            "pr_curve": f"{output_dir}/pr_curve.png"
        }
    }