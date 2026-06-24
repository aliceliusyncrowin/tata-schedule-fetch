CREATE TABLE IF NOT EXISTS tata_schedule_structured (
    schedule_date_ist DATE NOT NULL,
    time_retrieved TIMESTAMP WITH TIME ZONE NOT NULL,  
    period_end_ist TIMESTAMP WITHOUT TIME ZONE NOT NULL,

    time_block INTEGER NOT NULL,
    OA_REMC_OA_GNA  FLOAT NOT NULL,
    EMERGENCY_AS    FLOAT NOT NULL,
    SHORTFALL_AS     FLOAT NOT NULL,
    total_net_schd_amount FLOAT NOT NULL,
    remc_station_sch_amount FLOAT NOT NULL,
    remc_created_on_IST TIMESTAMP WITHOUT TIME ZONE NOT NULL,
    remc_revision_no INTEGER NOT NULL,
    full_schd_revision_no INTEGER NOT NULL,
    schedule_published_time_ist TIMESTAMP WITHOUT TIME ZONE NOT NULL,

    PRIMARY KEY (schedule_date_ist, period_end_ist, time_retrieved)
);
