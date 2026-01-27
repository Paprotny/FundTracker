# app/adapters/crypto.py

import requests
from datetime import datetime
from app.models import Asset

BINANCE_URL = "https://api.binance.com/api/v3/ticker/price"

def get_prices(assets: list[Asset]):
    results = []

    crypto_assets = [a for a in assets if a.market == "CRYPTO"]

    for asset in crypto_assets:
        symbol = f"{asset.symbol}USDT"
        r = requests.get(BINANCE_URL, params={"symbol": symbol})
        data = r.json()

        results.append({
            "asset": asset,
            "price": float(data["price"]),
            "timestamp": datetime.utcnow()
        })

    return results