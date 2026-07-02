CREATE TABLE IF NOT EXISTS tata_meter_actual_gen (
    time_period_end TIMESTAMP WITHOUT TIME ZONE NOT NULL,
    
    time_block INTEGER NOT NULL,
    generation FLOAT NOT NULL,
    source VARCHAR NOT NULL,

    PRIMARY KEY (time_period_end, time_block, source)
);
