import datetime
import psycopg2
import pandas as pd
import json, os
from psycopg2.extras import execute_values, Json
from zoneinfo import ZoneInfo


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


def create_structured_tata_schedule_table(conn):
    schema_path = os.path.join(os.path.dirname(__file__), "tata_schedule_structure.sql")
    with open(schema_path) as f:
        with conn.cursor() as cur:
            cur.execute(f.read())
    conn.commit()

PKEY_COLS = ("schedule_date_ist", "time_retrieved", "period_end_ist")
ALL_COLS = ("schedule_date_ist", "time_retrieved", "time_block", "period_end_ist", "OA_REMC_OA_GNA", "EMERGENCY_AS", "SHORTFALL_AS", "total_net_schd_amount", "remc_station_sch_amount", "remc_created_on_IST", "remc_revision_no", "full_schd_revision_no", "schedule_published_time_ist")


# def get_latest_actual_gen(conn):
#     sql = """
#         SELECT * FROM tata_meter_actual_gen
#         ORDER BY time_period_end DESC
#         LIMIT 1
#         """
#     with conn.cursor() as cur:
#         cur.execute(sql)
#         result = cur.fetchone()
#     if result:
#         print(f"Latest actual generation data: {result}")
#         return {
#             "time_period_end": result[0],
#             "time_block": result[1],
#             "actual_meter_generation": result[2],
#         }
#     else:
#         print("No actual generation data found.")
#         return None

def get_schedule_jsonb_rows(conn, count: int = 0):
    sql = """
        SELECT schedule_date_ist, time_retrieved, schedule_data
        FROM tata_schedule
        ORDER BY schedule_date_ist, time_retrieved
    """
    if count > 0:
        sql += f" LIMIT {count}"
    with conn.cursor() as cur:
        cur.execute(sql)
        rows = cur.fetchall()
    return [
        {
            "schedule_date_ist": row[0],
            "time_retrieved": row[1],
            "schedule_data": row[2],
        }
        for row in rows
    ]

def add_schedule_data(conn, data: list[tuple]):
    """
    Tuple must be in form  + order of ALL_COLS
    Only adds rows that do not already exist in the database.
    """

    sql = f"""
        INSERT INTO tata_schedule_structured ({", ".join(ALL_COLS)})
        VALUES %s
        ON CONFLICT ({", ".join(PKEY_COLS)}) DO NOTHING
        """

    with conn.cursor() as cur:
        execute_values(cur, sql, data)
    conn.commit()