from sqlalchemy.orm import Session
from datetime import datetime
from app import crud
from app.services.price_service import PriceService
from app.services.currency_service import CurrencyService
from app.adapters import gpw, crypto, de, l

class PriceUpdateService:

    @staticmethod
    def update_all_prices(db: Session) -> int:
        """
        Download prices from all adapters, convert to PLN, save to PriceCache.
        Overwrites previous PriceCache entries for each asset.
        Returns number of updated price records.
        """
        # Get all assets from database
        assets = crud.get_assets(db)

        # Split assets by market
        market_assets = {
            "GPW": [a for a in assets if a.market == "GPW"],
            "CRYPTO": [a for a in assets if a.market == "CRYPTO"],
            "DE": [a for a in assets if a.market == "DE"],
            "L": [a for a in assets if a.market == "L"],
        }

        adapters = {
            "GPW": gpw,
            "CRYPTO": crypto,
            "DE": de,
            "L": l
        }

        total_updated = 0

        # Loop through each adapter / market
        for market, asset_list in market_assets.items():
            if not asset_list:
                continue  # skip if no assets for this market

            adapter = adapters[market]

            # Get prices from adapter (returns list of dicts with 'asset', 'price', 'currency')
            prices_data = adapter.get_prices(asset_list)

            for data in prices_data:
                asset = data["asset"]
                price = data["price"]

                # Get current exchange rate to PLN
                rate_to_pln = CurrencyService.get_rate_to_pln(asset.currency)

                # Calculate value in PLN
                value_pln = price * rate_to_pln

                # Overwrite PriceCache for this asset
                # Remove old entries
                db.query(crud.PriceCache).filter(crud.PriceCache.asset_id == asset.id).delete()
                # Add new entry
                PriceService.add_price(db, asset, price=price, value_pln=value_pln)

                total_updated += 1

        # Handle bond assets separately
        bond_assets = [a for a in assets if a.type == "bond"]
        for asset in bond_assets:
            # This will calculate the bond value based on transactions + coupon history
            total_value = crud.update_bond_price_cache(db, asset)
            total_updated += 1

        return total_updated

