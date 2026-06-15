import logging
import azure.functions as func
import call_tata_schedule
import tata_schedule_blob
import datetime

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
        date = datetime.date.today().strftime("%Y-%m-%d")
        now = datetime.datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
        data = call_tata_schedule.get_utility_data(token, plant_name="Pavagada", date=date, schd_rev_no=-1)
        # logging.info(f"Utility data obtained for date:{date}\n{data}")

        logging.info('Python timer trigger function executed.')
        tata_schedule_blob.save_schedule_to_blob(data, date, now)

    except Exception as e:
        logging.error(f"Error in get_tata_scheduler: {e}")