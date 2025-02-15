import datetime
import logging

from pymongo import MongoClient, database

from almanacbot.ephemeris import Epehemeris


class MongoDBClient:
    """Class serving as MongoDB client"""

    def __init__(
        self,
        mongo_uri: str,
        username: str,
        password: str,
        db: str,
        authMechanism: str,
        ephemeris_collection: str,
    ):
        self.mongo_client: MongoClient = MongoClient(
            mongo_uri,
            username=username,
            password=password,
            authSource=db,
            authMechanism=authMechanism,
        )
        self.ephemeris_collection: str = ephemeris_collection
        self.mongo_db: database = self.mongo_client[db]

    def __del__(self):
        logging.info("Closing MongoDB...")
        self.mongo_client.close()
        logging.info("MongoDB properly closed.")

    def get_next_ephemeris(self, date: datetime) -> Epehemeris:
        p_day_of_year: dict = {
            "$project": {
                "date": 1,
                "todayDayOfYear": {"$dayOfYear": date},
                "leap": {
                    "$or": [
                        {"$eq": [0, {"$mod": [{"$year": "$date"}, 400]}]},
                        {
                            "$and": [
                                {"$eq": [0, {"$mod": [{"$year": "$date"}, 4]}]},
                                {"$ne": [0, {"$mod": [{"$year": "$date"}, 100]}]},
                            ]
                        },
                    ]
                },
                "dayOfYear": {"$dayOfYear": "$date"},
            }
        }

        p_leap_year: dict = {
            "$project": {
                "date": 1,
                "todayDayOfYear": 1,
                "dayOfYear": {
                    "$subtract": [
                        "$dayOfYear",
                        {
                            "$cond": [
                                {"$and": ["$leap", {"$gt": ["$dayOfYear", 59]}]},
                                1,
                                0,
                            ]
                        },
                    ]
                },
                "diff": {"$subtract": ["$dayOfYear", "$todayDayOfYear"]},
            }
        }

        p_past: dict = {
            "$project": {
                "diff": 1,
                "birthday": 1,
                "positiveDiff": {
                    "$cond": {
                        "if": {"$lt": ["$diff", 0]},
                        "then": {"$add": ["$diff", 365]},
                        "else": "$diff",
                    },
                },
            }
        }

        p_sort: dict = {"$sort": {"positiveDiff": 1}}

        p_first: dict = {
            "$group": {"_id": "first_birthday", "first": {"$first": "$$ROOT"}}
        }

        res = self.mongo_db[self.ephemeris_collection].aggregate(
            [p_day_of_year, p_leap_year, p_past, p_sort, p_first]
        )
        obj_id = res.next()["first"]["_id"]
        db_eph: dict = self.mongo_db[self.ephemeris_collection].find_one(
            {"_id": obj_id}
        )

        return Epehemeris.deserialize(db_eph)

    def get_next_eph_datetime(self, eph: Epehemeris, now: datetime) -> datetime:
        eph_datetime = eph.date
        eph_this_year = eph_datetime.replace(year=now.year, tzinfo=datetime.UTC)

        if eph_this_year < now:
            eph_next_year = eph_this_year.replace(year=eph_this_year.year + 1)
            return eph_next_year

        return eph_this_year
