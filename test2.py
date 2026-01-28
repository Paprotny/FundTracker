import yfinance as yf
import csv
from datetime import datetime

tickers = ["PKN.WA", "CDR.WA", "KGH.WA", "PZU.WA"]

results = []

for ticker in tickers:
    t = yf.Ticker(ticker)
    hist = t.history(period="1d")  # ostatni dzień
    if hist.empty:
        continue
    # Pobranie ostatniego wiersza
    last_row = hist.iloc[-1]  # iloc pozwala pobrać po pozycji
    close_price = last_row['Close']
    results.append({
        "symbol": ticker,
        "price": float(close_price),
        "timestamp": datetime.utcnow()
    })

# Zapis do CSV
filename = "yahoo_prices.csv"
fieldnames = ["symbol", "price", "timestamp"]

with open(filename, "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    for r in results:
        writer.writerow(r)

print(f"CSV zapisany do {filename}")