import os
import datetime
import psycopg2
import pandas as pd
from psycopg2.extras import execute_values, Json
from zoneinfo import ZoneInfo

IST = ZoneInfo("Asia/Kolkata")
UTC = ZoneInfo("UTC")

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


def create_live_estimate_table(conn):
    schema_path = os.path.join(
        os.path.dirname(__file__), "tata_schedule_json_schema.sql"
    )
    with open(schema_path) as f:
        with conn.cursor() as cur:
            cur.execute(f.read())
    conn.commit()


PKEY_COLS = (
   "schedule_date_ist", "time_retrieved"
)
ALL_COLS = {
    "schedule_date_ist", "time_retrieved", "schedule_data"
}

def upsert_schedule_json(
    conn,
    json: dict,
    date_ist: datetime.date,
    now_utc: pd.Timestamp,
):
    schedule_date_ist = date_ist if hasattr(date_ist, "year") else None
    update_set = "schedule_data = EXCLUDED.schedule_data"
    sql = f"""
        INSERT INTO tata_schedule (schedule_date_ist, time_retrieved, schedule_data)
        VALUES %s
        ON CONFLICT ({", ".join(PKEY_COLS)}) DO UPDATE SET {update_set}
    """
    with conn.cursor() as cur:
        execute_values(cur, sql, [(schedule_date_ist, now_utc, Json(json))] )
    conn.commit()

def get_latest_schedule_jsonb_by_date(conn, date_ist: datetime.date):
    """
    Fetches the latest schedule JSONB data for a specific date from the database.
    Returns None if no data is found for the given date.
    """
    sql = """
        SELECT schedule_data
        FROM tata_schedule
        WHERE schedule_date_ist = %s
        ORDER BY time_retrieved DESC
        LIMIT 1
    """
    with conn.cursor() as cur:
        cur.execute(sql, (date_ist,))
        result = cur.fetchone()
    return result[0] if result else None
