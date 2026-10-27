# FX Exchange Rate Pipeline: API to PostgreSQL to Power BI

## Overview
This project builds an automated data pipeline that collects daily exchange rates from a public API, stores them in PostgreSQL, and prepares them for analysis in Power BI. It tracks how the Indonesian Rupiah (IDR) moves against popular currencies for working and studying abroad, so a foreign salary can be translated into IDR over time.

## How this project was built
This is an AI-assisted learning project, built with Claude (by Anthropic). Claude suggested the topic and architecture and drafted most of the code and SQL. I set up the environment, the PostgreSQL database and the repository, ran and tested every step, and checked the results in the database. Issues found along the way, such as the API rate limit (HTTP 429) and a row returned outside the requested date range, were investigated and fixed during testing.

* **Data source:** [Frankfurter API](https://frankfurter.dev) v2, European Central Bank rates (`providers=ecb`). No API key is needed.
* **Coverage:** EUR as the base currency, quoted in IDR, USD, SGD, AUD, JPY, GBP, CAD, CHF, KRW and MYR. Daily business days from 2010-01-04 (about 43,000 rows).
* **Tech stack:** Python (requests, pandas, SQLAlchemy), PostgreSQL, Jupyter, Power BI.

## Pipeline

```
Frankfurter API (JSON) -> extract -> transform -> checks -> load (upsert) -> PostgreSQL -> Power BI
```

* **Extract:** requests one year at a time. Waits and retries with a growing delay when the API answers 429 (too many requests) or a server error.
* **Transform:** renames fields to match the table, converts types, removes invalid rates and duplicates.
* **Checks:** flags missing currencies, empty rates and daily moves above 15%. Problems are logged as warnings.
* **Load:** upserts rows (`INSERT ... ON CONFLICT DO UPDATE`), so running the pipeline twice never creates duplicates.
* **Incremental or backfill:** by default it fetches only from the latest stored date. `--start YYYY-MM-DD` reloads history.
* **Run log:** every run is recorded in `fx.etl_run_log` with its status, row count and message.

## Security
* Credentials are read from a local `.env` file, which is excluded from Git. `.env.example` shows the required variables.
* Two database roles with least privilege: `fx_etl` owns the `fx` schema and writes data, and `fx_reader` can only SELECT (for Power BI).

## Project structure
```
sql/        database setup scripts (placeholder passwords only)
src/        config, extract, transform, checks, load, pipeline
notebooks/  API exploration and tests
```

## How to run
1. **Clone and install** (developed with Python 3.12)
```bash
   git clone https://github.com/dennysproject/fx-exchange-rate-pipeline.git
   cd fx-exchange-rate-pipeline
   python -m venv .venv
   .venv\Scripts\activate
   pip install -r requirements.txt
```
2. **Create the database**
   * Run `sql/01_roles_and_schema.sql` as the PostgreSQL admin user, after replacing the placeholder passwords.
   * Run `sql/02_tables.sql` connected to `fx_analytics` as the `fx_etl` user.
3. **Configure credentials**
   * Copy `.env.example` to `.env` and fill in the values.
4. **Load the data**
```bash
   python -m src.pipeline --start 2010-01-01   # first run: full history
   python -m src.pipeline                      # later runs: new days only
```

## Check the result
```sql
SELECT COALESCE(quote_code, 'TOTAL') AS quote_code,
       COUNT(*) AS days,
       MIN(rate_date) AS first_date,
       MAX(rate_date) AS last_date
FROM fx.fact_exchange_rate
GROUP BY ROLLUP (quote_code)
ORDER BY quote_code;
```

Sample rows from `fx.fact_exchange_rate`:

| rate_date | base_code | quote_code | rate |
| :--- | :--- | :--- | ---: |
| 2025-01-02 | EUR | AUD | 1.66180 |
| 2025-01-02 | EUR | CAD | 1.48850 |
| 2025-01-02 | EUR | CHF | 0.93710 |
| 2025-01-02 | EUR | GBP | 0.83118 |
| 2025-01-02 | EUR | IDR | 16726.78000 |

## Known limitations
* Rates exist for business days only (the central bank does not publish on weekends and holidays).
* The pipeline is run by hand. A scheduler (Windows Task Scheduler or cron) is not set up yet.
* Quality checks report warnings but do not stop the load.

## Planned
* SQL views: IDR cross-rates, moving averages and daily changes.
* Power BI dashboard on a star schema (`dim_date`, `dim_currency`, fact table).

---
**Author:** Denny Ruchiat | [LinkedIn](https://www.linkedin.com/in/dennyruchiatatwork/)
