from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.services.portfolio_service import PortfolioService

router = APIRouter()

@router.get("/portfolio", summary="Get user's portfolio value")
def get_portfolio(db: Session = Depends(get_db)):
    """
    Returns the full portfolio summary in PLN using latest cached prices.
    """
    return PortfolioService.get_portfolio(db)
