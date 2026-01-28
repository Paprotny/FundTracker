from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.services.price_update_service import PriceUpdateService

router = APIRouter()

@router.get("/", summary="Update all prices from all markets")
def update_prices(db: Session = Depends(get_db)):
    total = PriceUpdateService.update_all_prices(db)
    return {"message": f"Prices updated for {total} assets"}