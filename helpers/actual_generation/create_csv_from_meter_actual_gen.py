import datetime
import pandas as pd


# Run from root
def create_csv_from_meter_actual_gen(actual_gen_file_path, end_date: datetime.datetime):
    """
    Uses all values from the actual generation file to create a CSV in the following format:
    Create csv in the following format:
    Period end, time block, date, actual_meter_generation
    """

    actual_gen_file = pd.read_csv(actual_gen_file_path)

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

        for block_num in range(1, 97):
            period_end_value = period_end_row.iloc[block_num]
            gen_value = row.iloc[block_num]
            records.append({
                'time_block': block_num,
                'period_end': period_end_value,
                'date': date.strftime("%Y-%m-%d"),
                'actual_meter_generation': gen_value
            })


    return pd.DataFrame(records)
 


def save_actual_gen_to_csv(data: pd.DataFrame, date: datetime.datetime):
    """
    Saves the actual generation data to a CSV file.
    """
    csv_filename = f"data/meter_actual_gen_{date.strftime('%Y-%m-%d')}.csv"
    data.to_csv(csv_filename, index=False)
    print(f"CSV saved: {csv_filename}")


if __name__ == "__main__":
    import sys
    end_date = datetime.datetime(2026, 6, 14)
    today = datetime.datetime.now()
    result_df = create_csv_from_meter_actual_gen("data/Pavagada_ActualGenData_FY27(Total).csv", end_date)
    save_actual_gen_to_csv(result_df, today)