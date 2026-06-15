CREATE TABLE IF NOT EXISTS tata_schedule (
    schedule_date_ist DATE NOT NULL,
    time_retrieved_utc TIMESTAMP WITH TIME ZONE NOT NULL,
    schedule_data JSONB NOT NULL,

    PRIMARY KEY (schedule_date_ist, time_retrieved_utc)
);
