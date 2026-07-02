import psycopg2
import os
from psycopg2.extras import execute_values


def get_connection():
    return psycopg2.connect(
        user=os.environ["POSTGRES_USER"],
        password=os.environ["POSTGRES_PASSWORD"],
        host=os.environ["POSTGRES_HOST"],
        port=os.environ["POSTGRES_PORT"],
        database=os.environ["POSTGRES_DB"],
        sslmode="require",
        connect_timeout=15,
    )


def create_structured_tata_schedule_table(conn):
    schema_path = os.path.join(os.path.dirname(__file__), "tata_schedule_structured.sql")
    with open(schema_path) as f:
        with conn.cursor() as cur:
            cur.execute(f.read())
    conn.commit()

def create_structured_tata_block_schedule_table(conn):
    schema_path = os.path.join(os.path.dirname(__file__), "tata_schedule_block_structured.sql")
    with open(schema_path) as f:
        with conn.cursor() as cur:
            cur.execute(f.read())
    conn.commit()

def create_structured_tata_block_gna_schedule_table(conn):
    schema_path = os.path.join(os.path.dirname(__file__), "tata_schedule_block_gna_structured.sql")
    with open(schema_path) as f:
        with conn.cursor() as cur:
            cur.execute(f.read())
    conn.commit()

COMBINED_PKEY_COLS = ("schedule_date_ist", "period_end_ist")
COMBINED_ALL_COLS = ("schedule_date_ist", "time_retrieved", "time_block", "period_end_ist", "OA_REMC_OA_GNA", "EMERGENCY_AS", "SHORTFALL_AS", "total_net_schd_amount", "remc_station_sch_amount", "remc_created_on_IST", "remc_revision_no", "full_schd_revision_no", "schedule_published_time_ist")


# def get_latest_actual_gen(conn):
#     sql = """
#         SELECT * FROM tata_meter_actual_gen
#         ORDER BY time_period_end DESC
#         LIMIT 1
#         """
#     with conn.cursor() as cur:
#         cur.execute(sql)
#         result = cur.fetchone()
#     if result:
#         print(f"Latest actual generation data: {result}")
#         return {
#             "time_period_end": result[0],
#             "time_block": result[1],
#             "actual_meter_generation": result[2],
#         }
#     else:
#         print("No actual generation data found.")
#         return None

def get_schedule_jsonb_rows(conn, count: int = 0):
    sql = """
        SELECT schedule_date_ist, time_retrieved, schedule_data
        FROM tata_schedule
        ORDER BY schedule_date_ist, time_retrieved
    """
    if count > 0:
        sql += f" LIMIT {count}"
    with conn.cursor() as cur:
        cur.execute(sql)
        rows = cur.fetchall()
    return [
        {
            "schedule_date_ist": row[0],
            "time_retrieved": row[1],
            "schedule_data": row[2],
        }
        for row in rows
    ]

def get_schedule_structured_rows(conn, count: int = 0):
    sql = """
        SELECT * FROM tata_schedule_structured
        ORDER BY schedule_date_ist, time_retrieved
    """
    if count > 0:
        sql += f" LIMIT {count}"
    with conn.cursor() as cur:
        cur.execute(sql)
        rows = cur.fetchall()
    return [
        {
            "schedule_date_ist": row[0],
            "time_retrieved": row[1],
            "period_end_ist": row[2],
            "time_block": row[3],
            "OA_REMC_OA_GNA": row[4],
            "EMERGENCY_AS": row[5],
            "SHORTFALL_AS": row[6],
            "total_net_schd_amount": row[7],
            "remc_station_sch_amount": row[8],
            "remc_created_on_IST": row[9],
            "remc_revision_no": row[10],
            "full_schd_revision_no": row[11],
            "schedule_published_time_ist": row[12],
        }
        for row in rows
    ]

def upsert_schedule_data(conn, data: list[tuple]):
    """
    Tuple must be in form  + order of ALL_COLS
    Only adds rows that do not already exist in the database.
    """
    update_set = ", ".join([f"{col} = EXCLUDED.{col}" for col in COMBINED_ALL_COLS if col not in COMBINED_PKEY_COLS])
    sql = f"""
        INSERT INTO tata_schedule_structured ({", ".join(COMBINED_ALL_COLS)})
        VALUES %s
        ON CONFLICT ({", ".join(COMBINED_PKEY_COLS)}) DO UPDATE SET
            {update_set} WHERE tata_schedule_structured.full_schd_revision_no <= EXCLUDED.full_schd_revision_no
        """

    with conn.cursor() as cur:
        execute_values(cur, sql, data)
    conn.commit()


BLOCK_PKEY_COLS = ("schedule_date_ist", "period_end_ist", "approval_no", "as_type_name", "energy_schedule_type_name", "energy_schedule_subtype_name", "px_exchange_type_name", "px_transaction_type_name")
BLOCK_ALL_COLS = ("schedule_date_ist", "time_retrieved", "period_end_ist", "time_block",
    "approval_no", "block_id",
    "link_name", "as_type_name", "energy_schedule_type_name", "energy_schedule_subtype_name",
    "px_exchange_type_name", "px_transaction_type_name",
    "buyer_acronym", "seller_acronym", "trader_acronym",
    "buyer_parent_state_util_acronym", "buyer_parent_discom_util_acronym",
    "buyer_unit_acronym", "seller_unit_acronym", "is_unit_wise_buyer", "is_unit_wise_seller",
    "data_integration_timing_type_name",
    "schd_amount", "poc_drawal_loss", "state_drawal_loss", "poc_injection_loss", "state_injection_loss",
    "discom_or_emb_in_state_drw_loss", "discom_or_emb_in_state_inj_loss",
    "total_drw_boundary_schd_amount", "total_inj_boundary_schd_amount", "total_reg_boundary_schd_amount",
    "full_schd_revision_no", "schedule_published_time_ist"
)

def upsert_block_schedule_data(conn, data: list[tuple]):
    """
    Tuple must be in form  + order of BLOCK_ALL_COLS. 
    Match extract_jsonb.flatten_block_jsonb return value.
    Only adds rows that do not already exist in the database.
    Do nothing if conflict on primary key.
    """
    update_set = ", ".join([f"{col} = EXCLUDED.{col}" for col in BLOCK_ALL_COLS if col not in BLOCK_PKEY_COLS])
    sql = f"""
        INSERT INTO tata_schedule_block_structured ({", ".join(BLOCK_ALL_COLS)})
        VALUES %s
        ON CONFLICT ({", ".join(BLOCK_PKEY_COLS)}) DO UPDATE SET
            {update_set} WHERE tata_schedule_block_structured.full_schd_revision_no <= EXCLUDED.full_schd_revision_no
        """

    with conn.cursor() as cur:
        execute_values(cur, sql, data)
    conn.commit()

BLOCK_GNA_PKEY_COLS = (
    "schedule_date_ist", "period_end_ist", "approval_no",
)
BLOCK_GNA_ALL_COLS = (
    "schedule_date_ist", "time_retrieved", "period_end_ist", "time_block",
    "approval_no", "block_id",
    "link_name", "revision_no", "remc_revision_no", "applicant_acronym", "is_remc_transaction",
    "from_date", "to_date", "contract_from_date", "contract_to_date",
    "buyer_acronym", "seller_acronym", "trader_acronym", "buyer_unit_acronym", "seller_unit_acronym",
    "buyer_trader_acronym", "seller_trader_acronym", "is_unit_wise_buyer", "is_unit_wise_seller",
    "buyer_generator_type_name", "seller_generator_type_name",
    "buyer_generator_subtype_name", "seller_generator_subtype_name",
    "buyer_parent_state_util_acronym", "buyer_parent_discom_util_acronym",
    "seller_parent_state_util_acronym", "seller_parent_discom_util_acronym",
    "contract_amount", "contract_dc_amount", "requisitioned_amount", "restriction_amount",
    "psm_reg_amount", "lpsc_reg_amount",
    "full_schd_revision_no", "schedule_published_time_ist",
)


def upsert_block_gna_schedule_data(conn, data: list[tuple]):
    """
    Tuple must be in the form + order of BLOCK_GNA_ALL_COLS (matches
    extract_block_jsonb.flatten_block_gna_jsonb's return value).
    Only adds rows that do not already exist in the database.
    """
    update_set = ", ".join([f"{col} = EXCLUDED.{col}" for col in BLOCK_GNA_ALL_COLS if col not in BLOCK_GNA_PKEY_COLS])
    sql = f"""
        INSERT INTO tata_schedule_block_gna_structured ({", ".join(BLOCK_GNA_ALL_COLS)})
        VALUES %s
        ON CONFLICT ({", ".join(BLOCK_GNA_PKEY_COLS)}) DO UPDATE SET
            {update_set} WHERE tata_schedule_block_gna_structured.full_schd_revision_no <= EXCLUDED.full_schd_revision_no
        """
    with conn.cursor() as cur:
        execute_values(cur, sql, data)
    conn.commit()
