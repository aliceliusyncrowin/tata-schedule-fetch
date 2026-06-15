import logging
import azure.functions as func
import call_tata_schedule
import db
import datetime
import pandas as pd

app = func.FunctionApp()

@app.timer_trigger(schedule="0 */15 * * * *", 
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
        # logging.info(f"Utility data obtained for date:{date_ist}\n{data}")

        logging.info('Python timer trigger function executed.')
        
        # Save to database
        logging.info("Saving schedule data to database...")
        conn = db.get_connection()
        db.create_live_estimate_table(conn)
        db.upsert_schedule_json(conn, data, date_ist, now_utc)
        logging.info("Schedule data saved to database successfully.")

    except Exception as e:
        logging.error(f"Error in get_tata_schedule: {e}")