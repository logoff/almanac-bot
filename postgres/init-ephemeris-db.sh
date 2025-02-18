#!/usr/bin/env bash
set -e

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    -- create schema and ephemeris table
    CREATE SCHEMA almanac;
    CREATE TABLE almanac.ephemeris (
        id serial primary key,
        date timestamp with time zone not null,
        text text not null,
        location point default null
     );

    -- init data
    -- INSERT INTO ephemeris(date, text, location) values (
    --    '2025-02-18 17:30:00 Europe/Madrid',
    --    'test text.',
    --    point(41.38291533569831, 2.169884207359594)
    --)
EOSQL
