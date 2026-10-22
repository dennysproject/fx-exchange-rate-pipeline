import time
from datetime import date

import requests

BASE_URL = "https://api.frankfurter.dev/v2"
PROVIDER = "ecb"
CURRENCIES = ["IDR", "USD", "SGD", "AUD", "JPY", "GBP", "CAD", "CHF", "KRW", "MYR"]


def fetch_rates(start_date, end_date, max_retries=5):
    """Fetch daily rates between two dates (as text, e.g. '2025-01-01'). Retries when rate limited."""
    for attempt in range(1, max_retries + 1):
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

        if response.status_code == 429 or response.status_code >= 500:
            retry_after = response.headers.get("Retry-After")
            wait = int(retry_after) if retry_after and retry_after.isdigit() else 10 * attempt
            print(f"Got {response.status_code}. Waiting {wait}s (attempt {attempt}/{max_retries})")
            time.sleep(wait)
            continue

        response.raise_for_status()
        return response.json()

    raise RuntimeError(f"Still failing after {max_retries} attempts: {start_date} to {end_date}")


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
        time.sleep(3)
    return rows


def fetch_currencies():
    """Fetch details (code, name) for the currencies we use, plus EUR."""
    response = requests.get(f"{BASE_URL}/currencies", timeout=30)
    response.raise_for_status()
    wanted = set(CURRENCIES) | {"EUR"}
    return [c for c in response.json() if c["iso_code"] in wanted]