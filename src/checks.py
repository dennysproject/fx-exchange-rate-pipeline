from src.extract import CURRENCIES


def check_rates(df, max_daily_move=0.15):
    """Return a list of warning messages. An empty list means all checks passed."""
    warnings = []

    missing = set(CURRENCIES) - set(df["quote_code"])
    if missing:
        warnings.append(f"Missing currencies: {sorted(missing)}")

    if df["rate"].isna().any():
        warnings.append("Some rates are empty")

    df = df.sort_values(["quote_code", "rate_date"])
    moves = df.groupby("quote_code")["rate"].pct_change().abs()
    big = df[moves > max_daily_move]
    if not big.empty:
        warnings.append(f"{len(big)} daily moves above {max_daily_move:.0%}")

    return warnings