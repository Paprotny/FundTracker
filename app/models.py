from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Date, Index, UniqueConstraint, Enum
from sqlalchemy.orm import relationship
from app.database import Base
from datetime import datetime
import enum

# -------------------------------
# ENUM FOR TRANSACTION TYPE
# -------------------------------
class TransactionTypeEnum(str, enum.Enum):
    buy = "buy"
    sell = "sell"

# -------------------------------
# MODELS
# -------------------------------
class Asset(Base):
    __tablename__ = "assets"
    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String, unique=True, index=True)
    market = Column(String)
    currency = Column(String)
    type = Column(String)  # stock / crypto / bond

    transactions = relationship("Transaction", back_populates="asset")
    prices = relationship("PriceCache", back_populates="asset")
    historical_prices = relationship(
        "HistoricalPrice",
        back_populates="asset",
        cascade="all, delete-orphan"
    )
    coupon_history = relationship(
        "BondCouponHistory",
        back_populates="asset",
        order_by="BondCouponHistory.start_date"
    )

class Transaction(Base):
    __tablename__ = "transactions"
    id = Column(Integer, primary_key=True, index=True)
    asset_id = Column(Integer, ForeignKey("assets.id"))
    quantity = Column(Float)
    price = Column(Float)
    date = Column(DateTime, default=datetime.utcnow)
    transaction_type = Column(Enum(TransactionTypeEnum), nullable=False)  # buy / sell

    asset = relationship("Asset", back_populates="transactions")

class PriceCache(Base):
    __tablename__ = "price_cache"
    id = Column(Integer, primary_key=True, index=True)
    asset_id = Column(Integer, ForeignKey("assets.id"))
    price = Column(Float)
    value_pln = Column(Float)
    timestamp = Column(DateTime, default=datetime.utcnow)

    asset = relationship("Asset", back_populates="prices")

class HistoricalPrice(Base):
    __tablename__ = "historical_prices"
    id = Column(Integer, primary_key=True, index=True)
    asset_id = Column(Integer, ForeignKey("assets.id"), nullable=False)
    asset = relationship("Asset", back_populates="historical_prices")

    date = Column(Date, nullable=False)
    price = Column(Float, nullable=False)
    value_pln = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        UniqueConstraint("asset_id", "date", name="uq_asset_date"),
        Index("idx_historical_asset_date", "asset_id", "date"),
    )
class BondCouponHistory(Base):
    __tablename__ = "bond_coupon_history"
    id = Column(Integer, primary_key=True)
    asset_id = Column(Integer, ForeignKey("assets.id"), nullable=False)
    start_date = Column(Date, nullable=False)  # date since when the coupon is valid
    coupon_rate = Column(Float, nullable=False)  # interest rate as a number e.g. 0.05

    asset = relationship("Asset", back_populates="coupon_history")