from sqlalchemy.orm import Session
from app.models import Asset, Transaction, PriceCache
from datetime import datetime
from sqlalchemy import desc

# -----------------------------
# ASSETS
# -----------------------------
def get_asset(db: Session, symbol: str):
    return db.query(Asset).filter(Asset.symbol == symbol).first()

def create_asset(db: Session, symbol: str, market: str, currency: str, type: str):
    asset = Asset(symbol=symbol, market=market, currency=currency, type=type)
    db.add(asset)
    db.commit()
    db.refresh(asset)
    return asset

def get_assets(db: Session):
    return db.query(Asset).all()


# -----------------------------
# TRANSACTIONS
# -----------------------------
def create_transaction(db: Session, asset: Asset, quantity: float, price: float, date: datetime = None):
    if date is None:
        date = datetime.utcnow()
    transaction = Transaction(asset=asset, quantity=quantity, price=price, date=date)
    db.add(transaction)
    db.commit()
    db.refresh(transaction)
    return transaction

def get_transactions_for_asset(db: Session, asset: Asset):
    return db.query(Transaction).filter(Transaction.asset_id == asset.id).all()


# -----------------------------
# PRICE CACHE
# -----------------------------
def add_price_to_cache(db: Session, asset: Asset, price: float, timestamp: datetime = None):
    if timestamp is None:
        timestamp = datetime.utcnow()
    price_record = PriceCache(asset=asset, price=price, timestamp=timestamp)
    db.add(price_record)
    db.commit()
    db.refresh(price_record)
    return price_record

def get_latest_price(db: Session, asset: Asset):
    return db.query(PriceCache).filter(PriceCache.asset_id == asset.id).order_by(PriceCache.timestamp.desc()).first()

def get_all_cached_prices(db):
    return db.query(PriceCache).all()
# -----------------------------
# CRUD FOR PRICE UPDATE
# -----------------------------
def get_or_create_asset(db: Session, symbol: str, market: str, currency: str, type: str):
    asset = db.query(Asset).filter(Asset.symbol == symbol).first()
    if asset is None:
        asset = Asset(symbol=symbol, market=market, currency=currency, type=type)
        db.add(asset)
        db.commit()
        db.refresh(asset)
    return asset