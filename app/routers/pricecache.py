from app.schemas import PriceCacheCreate, PriceCacheOut
from fastapi import APIRouter,Depends, HTTPException
from sqlalchemy.orm import Session
from app import crud, models
from app.database import get_db
from sqlalchemy import desc
from app.services.price_service import PriceService

router = APIRouter()
# GET /assets/{symbol}/price
@router.get("/{symbol}/price", response_model=PriceCacheOut)
def get_latest_price(symbol: str, db: Session = Depends(get_db)):
    asset = crud.get_asset(db, symbol)
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")
    price = crud.get_latest_price(db, asset)
    if not price:
        raise HTTPException(status_code=404, detail="No price found")
    return price

# POST /assets/{symbol}/price
@router.post("/{symbol}/price", response_model=PriceCacheOut)
def add_price(symbol: str, p_in: PriceCacheCreate, db: Session = Depends(get_db)):
    asset = crud.get_asset(db, symbol)
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")
    return crud.add_price_to_cache(db, asset, p_in.price, p_in.timestamp)

# GET /
@router.get("/latest", summary="Get latest price for each asset from PriceCache")
def get_latest_prices_endpoint(db: Session = Depends(get_db)):
    
    results = []
    
    
    assets = crud.get_assets(db)
    
    for asset in assets:
        last_price = crud.get_latest_price(db, asset)
        if last_price:
            results.append({
                "symbol": asset.symbol,
                "market": asset.market,
                "price": last_price.price,
                "currency": asset.currency,
                "timestamp": last_price.timestamp
            })
    
    return results

@router.get("/latest_prices", response_model=list[PriceCacheOut])
def latest_prices(db: Session = Depends(get_db)):
    latest_prices = PriceService.get_all_latest_prices(db)
    return latest_prices