-- Run as the postgres admin user. Replace the placeholder passwords.
-- Never commit real passwords.
CREATE ROLE fx_etl LOGIN PASSWORD 'change_me';
CREATE ROLE fx_reader LOGIN PASSWORD 'change_me_too';
CREATE DATABASE fx_analytics;

-- Now connect to the fx_analytics database and run the rest:
CREATE SCHEMA fx AUTHORIZATION fx_etl;
GRANT CONNECT ON DATABASE fx_analytics TO fx_etl, fx_reader;
GRANT USAGE ON SCHEMA fx TO fx_reader;
ALTER DEFAULT PRIVILEGES FOR ROLE fx_etl IN SCHEMA fx
  GRANT SELECT ON TABLES TO fx_reader;