from app.adapters import gpw, us, crypto, bonds
from app.database import SessionLocal
from app import crud

db = SessionLocal()

# pobieranie danych GPW
for data in gpw.get_prices():
    asset = crud.get_or_create_asset(db, data["symbol"], data["market"], data["currency"], data["type"])
    crud.add_price_to_cache(db, asset, data["price"], data["timestamp"])

db.close()