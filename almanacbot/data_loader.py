import configparser
import csv

from psycopg import OperationalError
import typer

from almanacbot import constants
from almanacbot.config import Configuration
from almanacbot.ephemeris import Ephemeris
from almanacbot.postgresql_client import PostgreSQLClient

config_parser: configparser = configparser.ConfigParser()


def read_configuration():
    # read configuration
    print("Reading configuration...")
    try:
        return Configuration(constants.CONFIG_FILE_NAME).config
    except ValueError:
        print("Error getting configuration: {err}")
        typer.Exit(1)
    print("Configuration correctly read.")


def main(
    csv_file_path: str = "init_db.csv",
):
    config: dict = read_configuration()

    with open(csv_file_path, "r") as csv_file:
        try:
            print("Connecting to PostgreSQL...")
            psql_client = PostgreSQLClient(
                user=config["postgresql"]["user"],
                password=config["postgresql"]["password"],
                hostname=config["postgresql"]["hostname"],
                database=config["postgresql"]["database"],
                ephemeris_table=config["postgresql"]["ephemeris_table"],
                logging_echo=bool(config["postgresql"]["logging_echo"]),
            )

            print("Checking for existing data...")
            if psql_client.count_ephemeris() > 0:
                confirmation: str = typer.confirm(
                    "There is data in the databse, are you sure you want to append more?"
                )
                if not confirmation:
                    print("Aborting!")
                    raise typer.Abort()

            print("Reading and inserting data...")
            csvReader = csv.reader(csv_file, delimiter=";")
            next(csvReader, None)  # skip header
            for row in csvReader:
                print(f"Read row: {row}")
                # Optional 3rd column: media_path
                media_path = row[2] if len(row) > 2 and row[2] else None
                psql_client.insert_ephemeris(
                    Ephemeris(
                        date=row[0],
                        text=row[1],
                        media_path=media_path,
                    )
                )
        except (OperationalError, ValueError) as exc:
            print(f"Error introducing CSV data to the DB: {exc}")
            typer.Exit(2)
