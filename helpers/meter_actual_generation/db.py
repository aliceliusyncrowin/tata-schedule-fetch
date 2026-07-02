import datetime
import psycopg2
import pandas as pd
import json, os
from psycopg2.extras import execute_values, Json
from zoneinfo import ZoneInfo

# TODO: add per block in meter data, per column

with open("local.settings.json", "r") as f:
    settings = json.load(f)["Values"]

for key, value in settings.items():
    os.environ[key] = value

database = os.getenv("POSTGRES_DB")
user = os.getenv("POSTGRES_USER")
password = os.getenv("POSTGRES_PASSWORD")
host = os.getenv("POSTGRES_HOST")


def get_connection():
    return psycopg2.connect(
        user=os.environ["POSTGRES_USER"],
        password=os.environ["POSTGRES_PASSWORD"],
        host=os.environ["POSTGRES_HOST"],
        port=os.environ["POSTGRES_PORT"],
        database=os.environ["POSTGRES_DB"],
        sslmode="require",
        connect_timeout=15,
    )


def create_actual_gen_table(conn):
    schema_path = os.path.join(os.path.dirname(__file__), "actual_gen.sql")
    with open(schema_path) as f:
        with conn.cursor() as cur:
            cur.execute(f.read())
    conn.commit()


PKEY_COLS = ("time_period_end", "time_block", "source")
ALL_COLS = {"time_period_end", "time_block", "generation", "source"}


def get_latest_actual_gen(conn):
    sql = """
        SELECT * FROM tata_meter_actual_gen
        ORDER BY time_period_end DESC
        LIMIT 1
        """
    with conn.cursor() as cur:
        cur.execute(sql)
        result = cur.fetchone()
    if result:
        print(f"Latest actual generation data: {result}")
        return {
            "time_period_end": result[0],
            "time_block": result[1],
            "generation": result[2],
            "source": result[3]
        }
    else:
        print("No actual generation data found.")
        return None


def add_meter_actual_generation(conn, data: list[tuple[datetime.datetime, int, float, str]]):
    """
    Tuple must be in form (time_period_end: datetime.datetime, time_block: int, generation: float, source: str)
    Only adds rows that do not already exist in the database.
    """

    sql = f"""
        INSERT INTO tata_meter_actual_gen (time_period_end, time_block, generation, source)
        VALUES %s
        ON CONFLICT ({", ".join(PKEY_COLS)}) DO NOTHING
        """

    with conn.cursor() as cur:
        execute_values(cur, sql, data)
    conn.commit()