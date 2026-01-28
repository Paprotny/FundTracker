from sqlalchemy.orm import Session
from app import crud
from app.models import Asset, PriceCache
from datetime import datetime


class PriceService:

    @staticmethod
    def add_price(
        db: Session,
        asset: Asset,
        price: float,
        value_pln: float = None,
        timestamp: datetime = None
    ) -> PriceCache:
        """
        Adds a new price record to PriceCache.

        - asset: Asset object
        - price: price in original currency
        - currency: original currency code (default "PLN")
        - value_pln: price converted to PLN (if None, will fallback to price for PLN)
        - timestamp: datetime of price (default now)
        """
        if timestamp is None:
            timestamp = datetime.utcnow().replace(microsecond=0)

        if value_pln is None:
            # If currency is PLN, value_pln = price; otherwise fallback to None
            value_pln = price if asset.currency.upper() == "PLN" else None

        price_record = PriceCache(
            asset=asset,
            price=price,
            value_pln=value_pln,
            timestamp=timestamp
        )

        db.add(price_record)
        db.commit()
        db.refresh(price_record)

        return price_record

    @staticmethod
    def get_latest_price(db: Session, asset: Asset):
        """Returning last price from cache."""
        return crud.get_latest_price(db, asset)

    @staticmethod
    def get_all_latest_prices(db: Session):
        """Returning all prices from assets."""
        assets = crud.get_assets(db)
        result = []
        for a in assets:
            latest = crud.get_latest_price(db, a)
            if latest:
                result.append(latest)
        return result
