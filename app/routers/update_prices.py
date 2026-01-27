from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app import crud
from app.adapters import gpw, l, de, crypto, bonds

router = APIRouter()

@router.get("/", summary="Update all prices from all markets")
def update_all_prices(db: Session = Depends(get_db)):

    assets = crud.get_assets(db)
    total_updated = 0

    sources = {
        "GPW": gpw.get_prices,
        "LSE": l.get_prices,
        "DE": de.get_prices,
        "CRYPTO": crypto.get_prices,
        "BONDS": bonds.get_prices,
    }

    for market, adapter in sources.items():
        market_assets = [a for a in assets if a.market == market]

        if not market_assets:
            continue

        price_data_list = adapter(market_assets)

        for data in price_data_list:
            crud.add_price_to_cache(
                db,
                data["asset"],
                data["price"],
                data["timestamp"]
            )
            total_updated += 1

    return {"message": f"Prices updated for {total_updated} assets"}