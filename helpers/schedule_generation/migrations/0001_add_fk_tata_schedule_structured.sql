ALTER TABLE tata_schedule_structured
ADD CONSTRAINT fk_tata_schedule_structured_tata_schedule
    FOREIGN KEY (schedule_date_ist, time_retrieved)
    REFERENCES tata_schedule (schedule_date_ist, time_retrieved);