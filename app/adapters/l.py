import yfinance as yf
from datetime import datetime,timedelta
from app.models import Asset
import pandas as pd

def get_prices(assets: list[Asset]):
    results = []
    for asset in assets:
        ticker = f"{asset.symbol}.L"
        t = yf.Ticker(ticker)
        hist = t.history(period="1d")
        if hist.empty:
            continue
        last_row = hist.iloc[-1]
        results.append({
            "asset": asset,
            "price": float(last_row['Close']),
            "timestamp": datetime.utcnow()
        })
    return results


def get_historical_prices(asset, start_date, end_date):
    """
    Get LSE stock historical daily prices from Yahoo Finance.
    Returns list of dicts: {"date": date, "price": float}
    """
    yf_symbol = f"{asset.symbol}.L"
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