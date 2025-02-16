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
    INSERT INTO ephemeris(date, text, location) values (
        '1899-11-29 12:00 Europe/Madrid',
        'Joan Gamper juntament amb els suïssos Otto Kunzle i Walter Wild, els anglesos John i William Parsons, l''alemany Otto Maier i els catalans Lluís d''Ossó, Bartomeu Terrades, l''aragonès Enric Ducay, Pere Cabot, Carles Pujol i Josep Llobet, es reuneixen al Gimnàs Solé per formar una associació que portarà el nom i l''escut de la ciutat: el Futbol Club Barcelona.',
        point(41.38291533569831, 2.169884207359594)
    );
    INSERT INTO ephemeris(date, text, location) values (
        '1957-09-24 12:00 Europe/Madrid',
        'S''inaugura el Camp Nou amb una missa solmne, una desfilada de diversos clubs de Catalunya i un partit entre el F.C. Barcelona i una selecció de jugadors de Varsòvia.',
        point(41.3808, 2.1228)
    );
    INSERT INTO ephemeris(date, text) values (
        '1999-11-29 12:00 Europe/Madrid',
        'El F.C. Barcelona celebra el seu centenari.'
    );
    INSERT INTO ephemeris(date, text, location) values (
        '1950-02-16 17:30:00 Europe/Madrid',
        'test.',
        point(41.38291533569831, 2.169884207359594)
    )
EOSQL
