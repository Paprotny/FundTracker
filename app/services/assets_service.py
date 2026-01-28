from sqlalchemy.orm import Session
from app import crud
from app.models import Asset

class AssetService:

    @staticmethod
    def create_asset(db: Session, symbol: str, market: str, currency: str, type: str) -> Asset:
        """Creating asset or returning existing one (business validation)."""
        existing = crud.get_asset(db, symbol)
        if existing:
            return existing
        return crud.create_asset(db, symbol, market, currency, type)

    @staticmethod
    def list_assets(db: Session):
        """Return all assets from db."""
        return crud.get_assets(db)

    @staticmethod
    def get_asset_by_symbol(db: Session, symbol: str):
        """Returning single asset by symbol."""
        return crud.get_asset(db, symbol)
