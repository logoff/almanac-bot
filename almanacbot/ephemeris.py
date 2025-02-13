import datetime

from typing import Self


class Epehemeris:
    DATE_FORMAT: str = "%Y-%m-%d %H:%M:%S"

    class Location:
        def __init__(self, latitude: float, longitude: float):
            self._latitude: float = latitude
            self._longitude: float = longitude

        @property
        def latitude(self) -> float:
            return self._latitude

        @property
        def longitude(self) -> float:
            return self._longitude

    def __init__(self, date: datetime.datetime, text: str, location: Location):
        self._date: datetime.datetime = date
        self._text: str = text
        self._location: Epehemeris.Location = location

    @property
    def date(self) -> datetime.datetime:
        return self._date

    @property
    def text(self) -> str:
        return self._text

    @property
    def location(self) -> Location:
        return self._location

    def __str__(self):
        s: str = f"Date: {self.date}, text:{self.text}"
        if self.location:
            s = s + f" location: {self.location.latitude}, {self.location.latitude}"
        return s

    def serialize(self) -> dict:
        db_eph: dict = {}

        db_eph["date"] = self.date.strftime(format=Epehemeris.DATE_FORMAT)
        db_eph["text"] = self.text
        if self.location:
            db_eph["location"]["latitude"] = self.location.latitude
            db_eph["location"]["longitude"] = self.location.longitude
        return db_eph

    @staticmethod
    def deserialize(db_eph: dict) -> Self:
        location: Epehemeris.Location = None
        if "location" in db_eph:
            location = Epehemeris.Location(
                latitude=db_eph["location"]["latitude"],
                longitude=db_eph["location"]["longitude"],
            )
        return Epehemeris(
            date=db_eph["date"],
            text=db_eph["text"],
            location=location,
        )
