import datetime
import logging
import azure.functions as func
import call_tata_schedule
import db
import json
import pandas as pd
from flatten_schedule import db as flatten_db, extract_jsonb


app = func.FunctionApp()

@app.timer_trigger(schedule="%SCHEDULE_CRON%", 
                   arg_name="myTimer", 
                   run_on_startup=False,
              use_monitor=False) 
def get_tata_schedule(myTimer: func.TimerRequest) -> None:
    if myTimer.past_due:
        logging.info('The timer is past due!')
    logging.info("Starting get_tata_scheduler function")
    # --- Usage ---
    # Read credentials from environment variables, NOT hardcoded in the notebook
    try:
        # Get the encrypted password, token, and utility data
        logging.info("Encrypting password and fetching token...")
        encrypted_password = call_tata_schedule.encrypt_public_key()
        logging.info("Encrypted password obtained, now fetching token...")
        token = call_tata_schedule.get_token(encrypted_password)
        logging.info("Token obtained, now fetching utility data...")

        # TODO: Add date changes
        date_ist = pd.Timestamp.now(tz="Asia/Kolkata").date() # current date in IST
        now_utc = pd.Timestamp.now(tz="UTC")  # current time in UTC
        data = call_tata_schedule.get_utility_data(token, plant_name="Pavagada", date=date_ist.isoformat(), schd_rev_no=-1)
        
        # Save to database
        logging.info("Saving schedule data to database...")
        conn = db.get_connection()
        db.create_live_estimate_table(conn)
        db.upsert_schedule_json(conn, data, date_ist, now_utc)
        logging.info("Schedule data saved to database successfully.")

        # Flatten the JSONB data and save to structured tables
        logging.info("Flattening JSONB data and saving to structured tables...")
        flatten_db.create_structured_tata_schedule_table(conn)
        flatten_db.create_structured_tata_block_schedule_table(conn)
        flatten_db.create_structured_tata_block_gna_schedule_table(conn)

        total_rows = extract_jsonb.flatten_total_jsonb(now_utc, data)
        flatten_db.upsert_schedule_data(conn, total_rows)

        block_rows = extract_jsonb.flatten_block_jsonb(now_utc, data)
        flatten_db.upsert_block_schedule_data(conn, block_rows)

        block_gna_rows = extract_jsonb.flatten_block_gna_jsonb(now_utc, data)
        flatten_db.upsert_block_gna_schedule_data(conn, block_gna_rows)

        logging.info("Flattened data saved to structured tables successfully.")

    except Exception as e:
        logging.error(f"Error in get_tata_schedule: {e}")

@app.route(route="get_latest_jsonb_by_date", auth_level=func.AuthLevel.FUNCTION)
def get_latest_jsonb_by_date(req: func.HttpRequest) -> func.HttpResponse:
    try:
        date_str = req.params.get('date')
        
        if not date_str:
            return func.HttpResponse("Please provide a 'date' query parameter in YYYY-MM-DD format.", status_code=400)
        
        date_ist = pd.Timestamp(date_str).date()
        logging.info(f"Fetching latest schedule JSONB data for date: {date_ist}")
        conn = db.get_connection()
        data = db.get_latest_schedule_jsonb_by_date(conn, date_ist)
        
        if data is None:
            return func.HttpResponse(f"No schedule data found for date: {date_ist}", status_code=404)
        
        return func.HttpResponse(json.dumps(data), status_code=200)
    except Exception as e:
        logging.error(f"Error in get_latest_jsonb_by_date: {e}")
        return func.HttpResponse(f"Internal server error: {e}", status_code=500)
