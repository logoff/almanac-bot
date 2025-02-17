from typing import List

import sqlalchemy
from sqlalchemy import Select, create_engine, extract, select
from sqlalchemy.orm import Session

from almanacbot.ephemeris import Ephemeris


class PostgreSQLClient:
    """Class serving as PostgreSQL client"""

    def __init__(
        self,
        user: str,
        password: str,
        hostname: str,
        database: str,
        ephemeris_table: str,
        logging_echo: bool,
    ):
        self.engine = create_engine(
            f"postgresql+psycopg://{user}:{password}@{hostname}/{database}",
            echo=logging_echo,
        )
        self.ephemeris_table: str = ephemeris_table

    def get_today_ephemeris(self) -> List[Ephemeris]:
        query: Select = select(Ephemeris).filter(
            extract("DOY", Ephemeris.date) == extract("DOY", sqlalchemy.func.now())
        )
        session: Session = Session(self.engine)
        ephs: List[Ephemeris] = session.scalars(query).all()
        return ephs
