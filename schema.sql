CREATE TABLE IF NOT EXISTS tata_schedule (
    schedule_date_ist DATE NOT NULL,
    time_retrieved TIMESTAMP WITH TIME ZONE NOT NULL,
    time_retrieved_ist TIMESTAMP GENERATED ALWAYS AS (time_retrieved AT TIME ZONE 'Asia/Kolkata') STORED,
    schedule_data JSONB NOT NULL,

    PRIMARY KEY (schedule_date_ist, time_retrieved)
);
