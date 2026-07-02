CREATE TABLE IF NOT EXISTS tata_schedule_block_gna_structured (

    schedule_date_ist DATE NOT NULL,
    time_retrieved TIMESTAMP WITH TIME ZONE NOT NULL,
    period_end_ist TIMESTAMP WITHOUT TIME ZONE NOT NULL,
    time_block INTEGER NOT NULL,

    -- block_id is parsed from approval_no
    approval_no TEXT NOT NULL,
    block_id TEXT,

    link_name TEXT NOT NULL DEFAULT '',
    revision_no INTEGER NOT NULL,
    remc_revision_no INTEGER NOT NULL,
    applicant_acronym TEXT NOT NULL DEFAULT '',
    is_remc_transaction BOOLEAN NOT NULL DEFAULT FALSE,
    from_date DATE NOT NULL,
    to_date DATE NOT NULL,
    contract_from_date DATE NOT NULL,
    contract_to_date DATE NOT NULL,

    buyer_acronym TEXT NOT NULL DEFAULT '',
    seller_acronym TEXT NOT NULL DEFAULT '',
    trader_acronym TEXT NOT NULL DEFAULT '',
    buyer_unit_acronym TEXT NOT NULL DEFAULT '',
    seller_unit_acronym TEXT NOT NULL DEFAULT '',
    buyer_trader_acronym TEXT NOT NULL DEFAULT '',
    seller_trader_acronym TEXT NOT NULL DEFAULT '',
    is_unit_wise_buyer BOOLEAN NOT NULL DEFAULT FALSE,
    is_unit_wise_seller BOOLEAN NOT NULL DEFAULT FALSE,
    buyer_generator_type_name TEXT NOT NULL DEFAULT '',
    seller_generator_type_name TEXT NOT NULL DEFAULT '',
    buyer_generator_subtype_name TEXT NOT NULL DEFAULT '',
    seller_generator_subtype_name TEXT NOT NULL DEFAULT '',
    buyer_parent_state_util_acronym TEXT NOT NULL DEFAULT '',
    buyer_parent_discom_util_acronym TEXT NOT NULL DEFAULT '',
    seller_parent_state_util_acronym TEXT NOT NULL DEFAULT '',
    seller_parent_discom_util_acronym TEXT NOT NULL DEFAULT '',

    -- group wise gna
    contract_amount FLOAT NOT NULL,
    contract_dc_amount FLOAT NOT NULL,
    requisitioned_amount FLOAT NOT NULL,
    restriction_amount FLOAT NOT NULL,
    psm_reg_amount FLOAT,
    lpsc_reg_amount FLOAT,

    full_schd_revision_no INTEGER NOT NULL,
    schedule_published_time_ist TIMESTAMP WITHOUT TIME ZONE NOT NULL,

    PRIMARY KEY (
        schedule_date_ist, period_end_ist, approval_no
    ),
    FOREIGN KEY (schedule_date_ist, time_retrieved) 
        REFERENCES tata_schedule (schedule_date_ist, time_retrieved)
)