# app/adapters/europe.py
from datetime import datetime

def get_prices(assets):
    results = []

    for asset in assets:
        results.append({
            "asset": asset,
            "price": 100.0,
            "timestamp": datetime.utcnow()
        })

    return results