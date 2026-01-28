from sqlalchemy.orm import Session
from app.models import Asset, Transaction, PriceCache, HistoricalPrice, TransactionTypeEnum, BondCouponHistory
from datetime import datetime,date

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
def create_transaction(db: Session, asset: Asset, quantity: float, price: float, transaction_type: str, date: datetime = None):
    transaction_type=TransactionTypeEnum(transaction_type.lower())
    if date is None:
        date = datetime.utcnow()
    transaction = Transaction(asset=asset, quantity=quantity, price=price, transaction_type=transaction_type, date=date)
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
def update_bond_price_cache(db: Session, asset: Asset) -> float:
    """
    Calculate and update the PriceCache for a bond asset based on its transactions and coupon history.
    Overwrites previous PriceCache entries for this bond.
    Returns the total value of the bond holdings.
    """
    transactions = get_transactions_for_asset(db, asset)
    if not transactions:
        return 0.0

    # Download coupon history
    coupon_history = (
        db.query(BondCouponHistory)
        .filter(BondCouponHistory.asset_id == asset.id)
        .order_by(BondCouponHistory.start_date)
        .all()
    )

    total_value = 0.0
    now = datetime.utcnow().date()

    for t in transactions:
        t_date = t.date.date()
        value = t.quantity * t.price

        if asset.symbol.startswith("EDO"):  # Yearly capitalization
            current_date = t_date
            for i, coupon in enumerate(coupon_history):
                next_start = coupon_history[i + 1].start_date if i + 1 < len(coupon_history) else now
                if coupon.start_date > now:
                    break
                start = max(current_date, coupon.start_date)
                end = min(next_start, now)
                years = (end - start).days / 365.0
                if years > 0:
                    value *= (1 + coupon.coupon_rate) ** years
                current_date = next_start

        elif asset.symbol.startswith("TOS"):  # No yearly capitalization
            current_date = t_date
            for i, coupon in enumerate(coupon_history):
                next_start = coupon_history[i + 1].start_date if i + 1 < len(coupon_history) else now
                if coupon.start_date > now:
                    break
                start = max(current_date, coupon.start_date)
                end = min(next_start, now)
                years = (end - start).days / 365.0
                if years > 0:
                    value *= (1 + coupon.coupon_rate * years)
                current_date = next_start

        if t.transaction_type == TransactionTypeEnum.buy:
            total_value += value
        elif t.transaction_type == TransactionTypeEnum.sell:
            total_value -= value

    # **Delete old PriceCache entries for this bond**
    db.query(PriceCache).filter(PriceCache.asset_id == asset.id).delete()

    # Save new PriceCache entry
    price_cache = PriceCache(asset=asset, price=total_value, value_pln=total_value)
    db.add(price_cache)
    db.commit()
    db.refresh(price_cache)

    return total_value
# -----------------------------
# HISTORICAL PRICES
# -----------------------------

def get_historical_price(db: Session, asset: Asset, date: date):
    return (
        db.query(HistoricalPrice)
        .filter(
            HistoricalPrice.asset_id == asset.id,
            HistoricalPrice.date == date
        )
        .first()
    )


def get_historical_prices_for_asset(db: Session, asset: Asset):
    return (
        db.query(HistoricalPrice)
        .filter(HistoricalPrice.asset_id == asset.id)
        .order_by(HistoricalPrice.date)
        .all()
    )


def get_existing_historical_dates(db: Session, asset: Asset) -> set:
    rows = (
        db.query(HistoricalPrice.date)
        .filter(HistoricalPrice.asset_id == asset.id)
        .all()
    )
    return {r[0] for r in rows}


def add_historical_price(
    db: Session,
    asset: Asset,
    date: date,
    price: float,
    value_pln: float
):
    record = HistoricalPrice(
        asset=asset,
        date=date,
        price=price,
        value_pln=value_pln
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return record

def calculate_bond_value_on_date(db: Session, asset: Asset, target_date: date) -> float:
    """
    Calculate the total value of a bond asset on a specific date.
    Uses transactions and bond coupon history.
    """
    transactions = get_transactions_for_asset(db, asset)
    if not transactions:
        return 0.0

    coupon_history = db.query(BondCouponHistory).filter(
        BondCouponHistory.asset_id == asset.id
    ).order_by(BondCouponHistory.start_date).all()

    total_value = 0.0

    for t in transactions:
        t_date = t.date.date()
        if t_date > target_date:
            continue  # transaction after the target date is ignored

        value = t.quantity * t.price
        current_date = t_date

        if asset.symbol.startswith("EDO"):  # Yearly capitalization
            for i, coupon in enumerate(coupon_history):
                next_start = coupon_history[i + 1].start_date if i + 1 < len(coupon_history) else target_date
                if coupon.start_date > target_date:
                    break
                start = max(current_date, coupon.start_date)
                end = min(next_start, target_date)
                years = (end - start).days / 365.0
                if years > 0:
                    value *= (1 + coupon.coupon_rate) ** years
                current_date = next_start
        elif asset.symbol.startswith("TOS"):  # No yearly capitalization
            for i, coupon in enumerate(coupon_history):
                next_start = coupon_history[i + 1].start_date if i + 1 < len(coupon_history) else target_date
                if coupon.start_date > target_date:
                    break
                start = max(current_date, coupon.start_date)
                end = min(next_start, target_date)
                years = (end - start).days / 365.0
                if years > 0:
                    value *= (1 + coupon.coupon_rate * years)
                current_date = next_start

        if t.transaction_type == TransactionTypeEnum.buy:
            total_value += value
        elif t.transaction_type == TransactionTypeEnum.sell:
            total_value -= value

    return total_value