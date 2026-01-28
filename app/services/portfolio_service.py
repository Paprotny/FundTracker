from sqlalchemy.orm import Session
from app import crud
from datetime import datetime

class PortfolioService:
    """
    Service to calculate user's portfolio value based on transactions and latest cached prices.
    All values are aggregated in PLN using PriceCache.value_pln.
    """

    @staticmethod
    def get_portfolio(db: Session):
        """
        Returns the portfolio summary:
        - total portfolio value in PLN
        - each asset with quantity, last price, value in PLN, and percentage of portfolio
        """
        assets = crud.get_assets(db)  # get all assets
        portfolio = []
        total_value = 0.0

        # First, calculate the value of each asset
        for asset in assets:
            transactions = crud.get_transactions_for_asset(db, asset)
            if not transactions:
                continue  # skip assets without transactions

            # Total quantity owned
            total_quantity = sum(t.quantity for t in transactions)

            # Get the latest price from PriceCache (in PLN)
            latest_price_record = crud.get_latest_price(db, asset)
            if latest_price_record is None:
                continue  # skip if no price available

            last_price = latest_price_record.price
            value_pln = latest_price_record.value_pln * total_quantity

            portfolio.append({
                "symbol": asset.symbol,
                "market": asset.market,
                "currency": asset.currency,
                "quantity": total_quantity,
                "last_price": last_price,
                "value_pln": value_pln
            })

            total_value += value_pln

        # Now, calculate percentage of total portfolio
        for item in portfolio:
            item["percentage"] = round((item["value_pln"] / total_value) * 100, 2) if total_value > 0 else 0.0

        return {
            "total_value_pln": round(total_value, 2),
            "assets": portfolio
        }