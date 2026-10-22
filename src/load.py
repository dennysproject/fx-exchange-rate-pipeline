from sqlalchemy import text

UPSERT_CURRENCY = text("""
INSERT INTO fx.dim_currency (currency_code, currency_name)
VALUES (:currency_code, :currency_name)
ON CONFLICT (currency_code)
DO UPDATE SET currency_name = EXCLUDED.currency_name
""")

UPSERT_RATE = text("""
INSERT INTO fx.fact_exchange_rate (rate_date, base_code, quote_code, rate)
VALUES (:rate_date, :base_code, :quote_code, :rate)
ON CONFLICT (rate_date, base_code, quote_code)
DO UPDATE SET rate = EXCLUDED.rate, loaded_at = now()
""")


def load_currencies(engine, df):
    records = df.to_dict(orient="records")
    with engine.begin() as conn:
        conn.execute(UPSERT_CURRENCY, records)
    return len(records)


def load_rates(engine, df):
    records = df.to_dict(orient="records")
    with engine.begin() as conn:
        conn.execute(UPSERT_RATE, records)
    return len(records)


def get_last_date(engine):
    with engine.connect() as conn:
        return conn.execute(text("SELECT max(rate_date) FROM fx.fact_exchange_rate")).scalar()


def start_run(engine):
    with engine.begin() as conn:
        return conn.execute(text(
            "INSERT INTO fx.etl_run_log (started_at, status) VALUES (now(), 'running') RETURNING run_id"
        )).scalar()


def finish_run(engine, run_id, rows_loaded, status, message):
    with engine.begin() as conn:
        conn.execute(
            text("""
                UPDATE fx.etl_run_log
                SET finished_at = now(), rows_loaded = :rows_loaded,
                    status = :status, message = :message
                WHERE run_id = :run_id
            """),
            {"run_id": run_id, "rows_loaded": rows_loaded, "status": status, "message": message},
        )