from sqlalchemy.orm import Session
from datetime import datetime
from app import crud
from app.models import Transaction, Asset

class TransactionService:

    @staticmethod
    def create_transaction(db: Session, asset: Asset, quantity: float, price: float, transaction_type: str, date: datetime = None) -> Transaction:
        """Create a new transaction for an asset."""
        return crud.create_transaction(db, asset, quantity, price, transaction_type, date)

    @staticmethod
    def get_transactions_for_asset(db: Session, asset: Asset):
        """Return all transactions for an asset."""
        return crud.get_transactions_for_asset(db, asset)
