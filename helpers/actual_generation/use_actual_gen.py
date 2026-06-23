import pandas as pd
import datetime
from . import db

def get_db_list_from_meter_actual_gen(file_path, end_date: datetime.datetime) -> list[tuple[datetime.datetime, int, float]]:
    """
    Uses all values from the actual generation file to create a list of tuples in the following format:
    (time_period_end, time_block, actual_meter_generation)
    Use for db uploads
    """

    actual_gen_file = pd.read_csv(file_path)

    # Period end, time block, date, actual_meter_generation
    period_end_row = actual_gen_file.iloc[0][:97]

    records = []

    for i, row in actual_gen_file.iterrows():
        if i == 0:
            continue
        date = pd.to_datetime(row.iloc[0])

        if date > end_date:
            break

        print(f"Processing date = {date}")

        for time_block in range(1, 97):
        
            period_end_str = period_end_row.iloc[time_block]
            hours, minutes, seconds = map(int, period_end_str.split(':'))
            
            if hours == 24:
                time_period_end = datetime.datetime(date.year, date.month, date.day) + datetime.timedelta(days=1)
            else:
                time_period_end = datetime.datetime(date.year, date.month, date.day, hours, minutes)
            
            actual_meter_generation = row.iloc[time_block]

            # print(f"Block {time_block}: Period End = {time_period_end}, Generation = {actual_meter_generation}")
            records.append((
                time_period_end,
                time_block,
                actual_meter_generation
            ))

    return records

def get_latest_unadded_meter_actual_gen(records) -> list[tuple[datetime.datetime, int, float]]:
    """
    Returns a list of tuples that are not already added to the database. Only returns records that are after the latest record in the database.
    """

    conn = db.get_connection()

    latest_records = db.get_latest_actual_gen(conn)

    latest_time_period_end = latest_records["time_period_end"] if latest_records else None
    
    if latest_time_period_end:
        records = [r for r in records if r[0] > latest_time_period_end]
    
    conn.close()
    return records