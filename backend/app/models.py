from sqlalchemy import Column, Integer, String, DECIMAL, ForeignKey, JSON, TIMESTAMP
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from .database import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    role = Column(String(20), nullable=False)  # producer / consumer
    password_hash = Column(String(200), nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now())

    products = relationship("Product", back_populates="producer")
    requests = relationship("Request", back_populates="consumer")

class Product(Base):
    __tablename__ = "products"
    id = Column(Integer, primary_key=True, index=True)
    producer_id = Column(Integer, ForeignKey("users.id"))
    name = Column(String(100), nullable=False)
    price = Column(DECIMAL(10,2), nullable=False)
    quantity = Column(Integer, nullable=False)
    specs = Column(JSON)
    domain = Column(String(50), nullable=True, index=True)
    created_at = Column(TIMESTAMP, server_default=func.now())

    producer = relationship("User", back_populates="products")

class Request(Base):
    __tablename__ = "requests"
    id = Column(Integer, primary_key=True, index=True)
    consumer_id = Column(Integer, ForeignKey("users.id"))
    product_name = Column(String(100))
    quantity = Column(Integer, nullable=False)
    budget = Column(DECIMAL(10,2))
    specs = Column(JSON)
    created_at = Column(TIMESTAMP, server_default=func.now())

    consumer = relationship("User", back_populates="requests")

class Negotiation(Base):
    __tablename__ = "negotiations"
    id = Column(Integer, primary_key=True, index=True)
    producer_id = Column(Integer, ForeignKey("users.id"))
    consumer_id = Column(Integer, ForeignKey("users.id"))
    round = Column(Integer, nullable=False)
    offer = Column(JSON)
    consumer_satisfaction = Column(DECIMAL(5,2))
    producer_satisfaction = Column(DECIMAL(5,2))
    status = Column(String(20), default="pending")
    created_at = Column(TIMESTAMP, server_default=func.now())
