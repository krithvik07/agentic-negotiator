from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import Request
from pydantic import BaseModel

router = APIRouter()

class RequestCreate(BaseModel):
    consumer_id: int
    product_name: str
    quantity: int
    budget: float
    specs: dict = {}

@router.post("/submit")
def submit_request(req: RequestCreate, db: Session = Depends(get_db)):
    db_req = Request(
        consumer_id=req.consumer_id,
        product_name=req.product_name,
        quantity=req.quantity,
        budget=req.budget,
        specs=req.specs
    )
    db.add(db_req)
    db.commit()
    db.refresh(db_req)
    return {"id": db_req.id, "product_name": db_req.product_name}
