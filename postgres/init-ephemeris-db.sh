#!/usr/bin/env bash
set -e

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    -- create schema and ephemeris table
    CREATE SCHEMA almanac;
    CREATE TABLE almanac.ephemeris (
        id serial primary key,
        date timestamp with time zone not null,
        text text not null,
        media_path text default null,
        last_tweeted_at timestamp with time zone default null
     );

    -- create index for efficient month+day queries
    CREATE INDEX idx_ephemeris_month_day
    ON almanac.ephemeris (EXTRACT(MONTH FROM date), EXTRACT(DAY FROM date));
EOSQL
