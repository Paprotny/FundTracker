from datetime import date, datetime, timedelta
from sqlalchemy.orm import Session

from app import crud
from app.models import Asset, HistoricalPrice, BondCouponHistory
from app.services.currency_service import CurrencyService
from app.adapters import gpw, crypto, de, l


class HistoricalPriceService:
    """
    Service responsible for downloading and storing daily historical prices
    for assets owned by the user.
    """

    @staticmethod
    def update_all_assets_history(db: Session) -> int:
        """
        Update historical prices for all assets that have at least one transaction.
        Returns number of newly created historical price records.
        """
        assets = crud.get_assets(db)
        total_created = 0

        for asset in assets:
            # Skip assets without transactions
            transactions = crud.get_transactions_for_asset(db, asset)
            if not transactions:
                continue

            created = HistoricalPriceService.update_asset_history(db, asset)
            total_created += created

        return total_created

    @staticmethod
    def update_asset_history(db: Session, asset: Asset) -> int:
        """
        Update historical prices for a single asset.
        For stocks/crypto: download missing dates.
        For bonds: generate daily prices from transactions and coupon history.
        """
        # Determine date range
        transactions = crud.get_transactions_for_asset(db, asset)
        if not transactions:
            return 0

        start_date = min(t.date.date() for t in transactions)
        end_date = date.today()

        existing_dates = crud.get_existing_historical_dates(db, asset)
        all_dates = {start_date + timedelta(days=i) for i in range((end_date - start_date).days + 1)}
        missing_dates = sorted(all_dates - existing_dates)

        if not missing_dates:
            return 0

        created = 0

        if asset.type == "bond":
            # Generate prices for missing dates based on transactions + coupon history
            for d in missing_dates:
                total_value = crud.calculate_bond_value_on_date(db, asset, d)  # now trzeba zaimplementować
                crud.add_historical_price(
                    db=db,
                    asset=asset,
                    date=d,
                    price=total_value,
                    value_pln=total_value
                )
                created += 1
        else:
            # Stocks/crypto -> normal adapter
            adapter = HistoricalPriceService._get_adapter(asset.market)
            prices = adapter.get_historical_prices(asset, missing_dates[0], missing_dates[-1])
            for p in prices:
                price_date = p["date"]
                if price_date in existing_dates:
                    continue
                rate = CurrencyService.get_rate_to_pln(asset.currency, price_date)
                value_pln = p["price"] * rate
                crud.add_historical_price(
                    db=db,
                    asset=asset,
                    date=price_date,
                    price=p["price"],
                    value_pln=value_pln
                )
                created += 1

        return created


    @staticmethod
    def _get_adapter(market: str):
        """
        Return proper adapter based on asset market.
        """
        if market == "GPW":
            return gpw
        if market == "CRYPTO":
            return crypto
        if market == "DE":
            return de
        if market == "L":
            return l

        raise ValueError(f"Unsupported market: {market}")
