from app.schemas import TransactionCreate, TransactionOut
from fastapi import APIRouter,Depends, HTTPException
from sqlalchemy.orm import Session
from app import crud
from app.database import get_db

router=APIRouter()

# GET /transactions/{symbol}
@router.get("/{symbol}", response_model=list[TransactionOut])
def read_transactions(symbol: str, db: Session = Depends(get_db)):
    asset = crud.get_asset(db, symbol)
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")
    return crud.get_transactions_for_asset(db, asset)

# POST /transactions/{symbol}
@router.post("/{symbol}", response_model=TransactionOut)
def create_transaction(symbol: str, t_in: TransactionCreate, db: Session = Depends(get_db)):
    asset = crud.get_asset(db, symbol)
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")
    return crud.create_transaction(db, asset, t_in.quantity, t_in.price, t_in.date)
