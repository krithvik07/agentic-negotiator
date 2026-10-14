from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import Product
from pydantic import BaseModel
from typing import Optional

router = APIRouter()

class ProductCreate(BaseModel):
    producer_id: int
    name: str
    price: float
    quantity: int
    specs: dict = {}
    domain: Optional[str] = None

@router.post("/add")
def add_product(product: ProductCreate, db: Session = Depends(get_db)):
    db_product = Product(
        producer_id=product.producer_id,
        name=product.name,
        price=product.price,
        quantity=product.quantity,
        specs=product.specs,
        domain=product.domain
    )
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return {"id": db_product.id, "name": db_product.name}
