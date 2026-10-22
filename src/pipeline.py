import logging
import argparse
from datetime import date

from src.config import get_engine
from src.extract import fetch_all, fetch_currencies
from src.transform import rates_to_dataframe, currencies_to_dataframe
from src.checks import check_rates
from src.load import (
    load_currencies, load_rates, get_last_date, start_run, finish_run,
)

START_DATE = date(2010, 1, 1)

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger("fx_pipeline")


def run(start_override=None):
    engine = get_engine()
    run_id = start_run(engine)
    try:
        if start_override:
            start = start_override
        else:
            last_date = get_last_date(engine)
            start = last_date if last_date else START_DATE
        end = date.today()
        log.info("Run %s: fetching %s to %s", run_id, start, end)

        rows = fetch_all(start, end)
        if not rows:
            finish_run(engine, run_id, 0, "success", "No new data")
            log.info("No new data")
            return

        currencies_df = currencies_to_dataframe(fetch_currencies())
        rates_df = rates_to_dataframe(rows)

        warnings = check_rates(rates_df)
        for warning in warnings:
            log.warning(warning)

        load_currencies(engine, currencies_df)
        loaded = load_rates(engine, rates_df)

        message = "; ".join(warnings) if warnings else "OK"
        finish_run(engine, run_id, loaded, "success", message)
        log.info("Done: %s rows loaded", loaded)
    except Exception as error:
        finish_run(engine, run_id, 0, "failed", str(error)[:500])
        log.exception("Pipeline failed")
        raise


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Load exchange rates into PostgreSQL")
    parser.add_argument("--start", help="Backfill from this date (YYYY-MM-DD)")
    args = parser.parse_args()
    start_override = date.fromisoformat(args.start) if args.start else None
    run(start_override)