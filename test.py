import requests
from datetime import datetime

STOOQ_URL = "https://stooq.pl/q/l/"
gpw_tickers = ["PKN", "CDR"]

results = []

for ticker in gpw_tickers:
    params = {
        "s": ticker.lower(),
        "f": "sd2t2ohlcv",
        "h": "",
        "e": "csv"
    }
    r = requests.get(STOOQ_URL, params=params)
    r.raise_for_status()

    lines = r.text.strip().splitlines()
    if len(lines) < 2:
        continue

    headers = lines[0].split(",")
    data = lines[1].split(",")

    # Zamkniecie = Close
    if "Zamkniecie" in headers:
        close_index = headers.index("Zamkniecie")
        price = data[close_index]
        if price != "":
            results.append({
                "symbol": ticker.upper(),
                "price": float(price),
                "timestamp": datetime.utcnow()
            })

# Zapis do CSV
import csv
with open("gpw_prices.csv", "w", newline="", encoding="utf-8") as f:
    fieldnames = ["symbol", "price", "timestamp"]
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    for r in results:
        writer.writerow(r)

print("CSV zapisany z prawdziwymi cenami")