from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base
from datetime import datetime

class Asset(Base):
    __tablename__ = "assets"
    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String, unique=True, index=True)
    market = Column(String)
    currency = Column(String)
    type = Column(String)  # stock / crypto / bond

    transactions = relationship("Transaction", back_populates="asset")
    prices=relationship("PriceCache",back_populates="asset")

class Transaction(Base):
    __tablename__ = "transactions"
    id = Column(Integer, primary_key=True, index=True)
    asset_id = Column(Integer, ForeignKey("assets.id"))
    quantity = Column(Float)
    price = Column(Float)
    date = Column(DateTime, default=datetime.utcnow)

    asset = relationship("Asset", back_populates="transactions")


class PriceCache(Base):
    __tablename__ = "price_cache"
    id = Column(Integer, primary_key=True, index=True)
    asset_id = Column(Integer, ForeignKey("assets.id"))
    price = Column(Float)
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    asset=relationship("Asset",back_populates="prices")