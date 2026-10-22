import pandas as pd


def rates_to_dataframe(rows):
    """Turn the API rows into a clean table that matches fx.fact_exchange_rate."""
    df = pd.DataFrame(rows)
    df = df.rename(columns={"date": "rate_date", "base": "base_code", "quote": "quote_code"})
    df["rate_date"] = pd.to_datetime(df["rate_date"]).dt.date
    df["rate"] = pd.to_numeric(df["rate"], errors="coerce")
    df = df[df["rate"] > 0]
    df = df.drop_duplicates(subset=["rate_date", "base_code", "quote_code"])
    return df[["rate_date", "base_code", "quote_code", "rate"]]


def currencies_to_dataframe(currencies):
    """Turn the currency list into a table that matches fx.dim_currency."""
    df = pd.DataFrame(currencies)
    df = df.rename(columns={"iso_code": "currency_code", "name": "currency_name"})
    return df[["currency_code", "currency_name"]]