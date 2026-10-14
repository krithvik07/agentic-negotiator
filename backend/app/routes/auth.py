from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import User
from pydantic import BaseModel
import hashlib

router = APIRouter()

class UserCreate(BaseModel):
    name: str
    email: str
    role: str
    password: str

@router.post("/signup")
def signup(user: UserCreate, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == user.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already exists")
    hashed_pw = hashlib.sha256(user.password.encode()).hexdigest()
    db_user = User(
        name=user.name,
        email=user.email,
        role=user.role,
        password_hash=hashed_pw
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return {"id": db_user.id, "email": db_user.email, "role": db_user.role}

@router.post("/login")
def login(email: str, password: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=400, detail="Invalid credentials")
    hashed_pw = hashlib.sha256(password.encode()).hexdigest()
    if user.password_hash != hashed_pw:
        raise HTTPException(status_code=400, detail="Invalid credentials")
    return {"id": user.id, "email": user.email, "role": user.role}
