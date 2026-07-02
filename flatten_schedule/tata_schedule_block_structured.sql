CREATE TABLE IF NOT EXISTS tata_schedule_block_structured (
        
    schedule_date_ist DATE NOT NULL,
    time_retrieved TIMESTAMP WITH TIME ZONE NOT NULL,
    period_end_ist TIMESTAMP WITHOUT TIME ZONE NOT NULL,
    time_block INTEGER NOT NULL,

    -- block_id is parsed from approval_no
    approval_no TEXT NOT NULL DEFAULT '',
    block_id TEXT,

    link_name TEXT NOT NULL DEFAULT '',
    as_type_name TEXT NOT NULL,
    energy_schedule_type_name TEXT NOT NULL,
    energy_schedule_subtype_name TEXT NOT NULL,
    px_exchange_type_name TEXT NOT NULL,
    px_transaction_type_name TEXT NOT NULL,
    
    buyer_acronym TEXT NOT NULL DEFAULT '',
    seller_acronym TEXT NOT NULL DEFAULT '',
    trader_acronym TEXT NOT NULL DEFAULT '',
    buyer_parent_state_util_acronym TEXT NOT NULL DEFAULT '',
    buyer_parent_discom_util_acronym TEXT NOT NULL DEFAULT '',

    buyer_unit_acronym TEXT NOT NULL DEFAULT '',
    seller_unit_acronym TEXT NOT NULL DEFAULT '',
    is_unit_wise_buyer BOOLEAN NOT NULL DEFAULT FALSE,
    is_unit_wise_seller BOOLEAN NOT NULL DEFAULT FALSE,
    data_integration_timing_type_name TEXT NOT NULL DEFAULT 'NA',

    -- group wise schedule data
    schd_amount FLOAT NOT NULL,
    poc_drawal_loss FLOAT,
    state_drawal_loss FLOAT,
    poc_injection_loss FLOAT,
    state_injection_loss FLOAT,
    discom_or_emb_in_state_drw_loss FLOAT,
    discom_or_emb_in_state_inj_loss FLOAT,
    total_drw_boundary_schd_amount FLOAT,
    total_inj_boundary_schd_amount FLOAT,
    total_reg_boundary_schd_amount FLOAT,

    full_schd_revision_no INTEGER NOT NULL,
    schedule_published_time_ist TIMESTAMP WITHOUT TIME ZONE NOT NULL,

    PRIMARY KEY (
        schedule_date_ist, period_end_ist, approval_no, as_type_name, energy_schedule_type_name, energy_schedule_subtype_name, px_exchange_type_name, px_transaction_type_name
    ),
    FOREIGN KEY (schedule_date_ist, time_retrieved) 
        REFERENCES tata_schedule (schedule_date_ist, time_retrieved)

);