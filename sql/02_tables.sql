-- Run connected to fx_analytics as the fx_etl user.
CREATE TABLE IF NOT EXISTS fx.dim_currency (
  currency_code CHAR(3) PRIMARY KEY,
  currency_name TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS fx.fact_exchange_rate (
  rate_date  DATE NOT NULL,
  base_code  CHAR(3) NOT NULL,
  quote_code CHAR(3) NOT NULL REFERENCES fx.dim_currency(currency_code),
  rate       NUMERIC(18,6) NOT NULL,
  loaded_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
  PRIMARY KEY (rate_date, base_code, quote_code)
);

CREATE TABLE IF NOT EXISTS fx.etl_run_log (
  run_id BIGSERIAL PRIMARY KEY,
  started_at TIMESTAMPTZ,
  finished_at TIMESTAMPTZ,
  rows_loaded INT,
  status TEXT,
  message TEXT
);

CREATE INDEX IF NOT EXISTS idx_fact_quote_date
ON fx.fact_exchange_rate (quote_code, rate_date);