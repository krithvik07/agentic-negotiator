from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..database import get_db

router = APIRouter()

@router.post("/start")
def start_negotiation(request_id: int, db: Session = Depends(get_db)):
    # Placeholder for negotiation orchestrator
    # Later, connect LLM agents & satisfaction meter
    return {"message": f"Negotiation started for request {request_id}"}
