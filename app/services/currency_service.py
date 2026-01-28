import requests
from datetime import datetime, timedelta

class CurrencyService:
    """
    Service to download exchange rates vs PLN.
    Uses exchangerate.host API.
    """
    # map aliases to real currencies
    CURRENCY_MAP = {
        "USDT": "USD",
        "USDC": "USD",
        "BUSD": "USD"
    }
    _cache = {}
    _cache_expiry = timedelta(minutes=30)  # cache for 30 minutes

    @classmethod
    def get_rate_to_pln(cls, currency: str, date: datetime.date = None) -> float:
        """
        Get exchange rate to PLN.
        - currency: e.g. "USD", "EUR", "USDT"
        - date: optional, historical date. If None -> current rate with cache
        """
        currency = cls.CURRENCY_MAP.get(currency.upper(), currency.upper())

        # PLN -> PLN = 1
        if currency == "PLN":
            return 1.0

        now = datetime.utcnow()

        # Current rate caching
        if date is None and currency in cls._cache:
            rate, timestamp = cls._cache[currency]
            if now - timestamp < cls._cache_expiry:
                return rate

        # Build API URL
        if date is None:
            url = "https://api.exchangerate.host/latest"
        else:
            url = f"https://api.exchangerate.host/{date.isoformat()}"  # YYYY-MM-DD

        params = {"base": currency, "symbols": "PLN"}

        try:
            r = requests.get(url, params=params, timeout=5)
            r.raise_for_status()
            data = r.json()
            if "rates" not in data or "PLN" not in data["rates"]:
                raise ValueError(f"Invalid response from currency API: {data}")
            rate = float(data["rates"]["PLN"])
        except Exception as e:
            print(f"Error fetching rate for {currency} ({date}): {e}")
            rate = 1.0  # fallback

        # Save to cache only for current rates
        if date is None:
            cls._cache[currency] = (rate, now)

        return rate
