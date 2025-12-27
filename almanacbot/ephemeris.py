import datetime
from dataclasses import dataclass
from typing import Optional

from sqlalchemy import TIMESTAMP, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


@dataclass
class Ephemeris(Base):
    __tablename__ = "ephemeris"

    id: Mapped[int] = mapped_column(primary_key=True)
    date: Mapped[datetime.datetime] = mapped_column(TIMESTAMP(timezone=True))
    text: Mapped[str] = mapped_column(Text)
    media_path: Mapped[Optional[str]] = mapped_column(Text, default=None)
    last_tweeted_at: Mapped[Optional[datetime.datetime]] = mapped_column(
        TIMESTAMP(timezone=True), default=None
    )
