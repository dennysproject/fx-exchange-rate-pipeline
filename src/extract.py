import time
from datetime import date

import requests

BASE_URL = "https://api.frankfurter.dev/v2"
PROVIDER = "ecb"
CURRENCIES = ["IDR", "USD", "SGD", "AUD", "JPY", "GBP", "CAD", "CHF", "KRW", "MYR"]


def fetch_rates(start_date, end_date):
    """Fetch daily rates for CURRENCIES between two dates (as text, e.g. '2025-01-01')."""
    response = requests.get(
        f"{BASE_URL}/rates",
        params={
            "providers": PROVIDER,
            "from": start_date,
            "to": end_date,
            "quotes": ",".join(CURRENCIES),
        },
        timeout=30,
    )
    response.raise_for_status()
    return response.json()


def fetch_all(start_date, end_date):
    """Fetch a long period one year at a time. Dates must be date objects."""
    rows = []
    for year in range(start_date.year, end_date.year + 1):
        chunk_start = max(start_date, date(year, 1, 1))
        chunk_end = min(end_date, date(year, 12, 31))
        print(f"Fetching {chunk_start} to {chunk_end}")
        chunk = fetch_rates(chunk_start.isoformat(), chunk_end.isoformat())
        # The API can add the last rate before the start date. Keep only the range we asked for.
        chunk = [
            row for row in chunk
            if chunk_start.isoformat() <= row["date"] <= chunk_end.isoformat()
        ]
        rows.extend(chunk)
        time.sleep(1)
    return rows


def fetch_currencies():
    """Fetch details (code, name) for the currencies we use, plus EUR."""
    response = requests.get(f"{BASE_URL}/currencies", timeout=30)
    response.raise_for_status()
    wanted = set(CURRENCIES) | {"EUR"}
    return [c for c in response.json() if c["iso_code"] in wanted]