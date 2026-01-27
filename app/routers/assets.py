from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app import crud
from app.database import get_db
from app.schemas import AssetCreate, AssetOut  # Pydantic schemas

router = APIRouter()

# GET /assets
@router.get("/", response_model=list[AssetOut])
def read_assets(db: Session = Depends(get_db)):
    return crud.get_assets(db)

# GET /assets/{symbol}
@router.get("{symbol}", response_model=AssetOut)
def read_asset(symbol: str, db: Session = Depends(get_db)):
    asset = crud.get_asset(db, symbol)
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")
    return asset

# POST /assets
@router.post("/", response_model=AssetOut)
def create_asset(asset_in: AssetCreate, db: Session = Depends(get_db)):
    return crud.create_asset(db, asset_in.symbol, asset_in.market, asset_in.currency, asset_in.type)
