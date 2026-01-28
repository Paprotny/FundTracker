# app/adapters/crypto.py

import requests
from datetime import datetime,timedelta
from app.models import Asset
import yfinance as yf
import pandas as pd
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
def get_historical_prices(asset, start_date, end_date):
    """
    Get crypto historical daily prices from Yahoo Finance (USD pair).
    Returns list of dicts: {"date": date, "price": float}
    """
    yf_symbol = f"{asset.symbol}-USD"
    data = yf.download(
        yf_symbol,
        start=start_date,
        end=end_date + timedelta(days=1),
        interval="1d",
        progress=False,
        auto_adjust=True
    )

    if data.empty:
        return []

    close_series = data['Close']
    if isinstance(close_series, pd.DataFrame):
        close_series = close_series.iloc[:, 0]

    result = [
        {"date": d.date(), "price": float(p)}
        for d, p in zip(close_series.index, close_series)
        if pd.notna(p)
    ]

    return result