from app.database import SessionLocal
from app.services.historical_price_service import HistoricalPriceService

db = SessionLocal()

try:
    created = HistoricalPriceService.update_all_assets_history(db)
    print(f"Historical prices created: {created}")
finally:
    db.close()