import datetime

def _period_end_ist(schedule_date_ist: datetime.date, block_index: int) -> datetime.datetime:
    """
    Given schedule_date_ist and block_index (0-95), return the period_end_ist datetime."""
    period_end_time = datetime.time(
        hour=(block_index + 1) // 4 if (block_index + 1) < 96 else 0,
        minute=((block_index + 1) % 4) * 15
    )
    if period_end_time.hour == 0 and period_end_time.minute == 0:
        return datetime.datetime.combine(schedule_date_ist + datetime.timedelta(days=1), period_end_time)
    else:
        return datetime.datetime.combine(schedule_date_ist, period_end_time)

# TODO: confirm the block_id is always the last segment of the approval_no
def _block_id_from_approval_no(approval_no: str):
    if not approval_no:
        return None
    return approval_no.rsplit("_", 1)[-1]

def _at(series, block_index: int):
    """
    series may be None (field not populated), or a list of 96 values. Return the value at block_index, or None if series is None.
    """
    if series is None:
        return None
    return series[block_index]

def flatten_total_jsonb(time_retrieved, schedule_data: dict):
    """
    Convert one tata_schedule jsonb row into 96 rows.

    Return tuple matches:
    ("schedule_date_ist", "time_retrieved", "time_block", "period_end_ist", "OA_REMC_OA_GNA", "EMERGENCY_AS", "SHORTFALL_AS", "total_net_schd_amount", "station_sch_amount", "created_on_IST", "revision_no", "full_schd_revision_no", "schedule_published_time_ist")
    
    """
    response_body = schedule_data["data"]["ResponseBody"]

    # Group should always be PVG_TATARENEWABLE
    group = response_body["GroupWiseDataList"][0]

    schedule_date_ist = datetime.datetime.strptime(
        response_body["Date"],
        "%d-%m-%Y"
    )
    full_schd_revision_no = response_body["FullSchdRevisionNo"]
    schedule_published_time_ist = datetime.datetime.fromisoformat(
        response_body["SchedulePublishedTime"]
    )
    created_on_IST = datetime.datetime.fromisoformat(
        group["REMCDeclarationList"][0]["CreatedOn"]
    )
    revision_no = group["REMCDeclarationList"][0]["RevisionNo"]

    oa_remc_oa_gna_list = None
    emergency_as_list = None
    shortfall_as_list = None
    total_net_schd_amount_list = None
    station_sch_amount_list = None

    for item in group["NetScheduleSummary"]["NetSchdDataList"]:
        if item["EnergyScheduleTypeName"] == "OA_REMC" and item["EnergyScheduleSubTypeName"] == "OA_GNA":
            oa_remc_oa_gna_list = item["NetSchdAmount"]
        elif item["ASTypeName"] == "EMERGENCY":
            emergency_as_list = item["NetSchdAmount"]
        elif item["ASTypeName"] == "SHORTFALL":
            shortfall_as_list = item["NetSchdAmount"]
    
    total_net_schd_amount_list = group["NetScheduleSummary"]["TotalNetSchdAmount"]
    station_sch_amount_list = group["REMCDeclarationList"][0]["REMCDeclarationData"]["StationSchAmount"]

    if oa_remc_oa_gna_list is None:
        raise ValueError("OA_REMC_OA_GNA data not found in schedule_data")
    else:
        print(f"OA_REMC_OA_GNA data found: {oa_remc_oa_gna_list}")
    if emergency_as_list is None:
        raise ValueError("EMERGENCY_AS data not found in schedule_data")
    else: 
        print(f"EMERGENCY_AS data found: {emergency_as_list}")
    if shortfall_as_list is None:
        raise ValueError("SHORTFALL_AS data not found in schedule_data")    
    else:
        print(f"SHORTFALL_AS data found: {shortfall_as_list}")
    if total_net_schd_amount_list is None:
        raise ValueError("total_net_schd_amount data not found in schedule_data")
    else:
        print(f"total_net_schd_amount data found: {total_net_schd_amount_list}")
    if station_sch_amount_list is None:
        raise ValueError("station_sch_amount data not found in schedule_data")
    else:
        print(f"station_sch_amount data found: {station_sch_amount_list}")
    
    rows = []

    for block_index in range(96):
        period_end_ist = _period_end_ist(schedule_date_ist, block_index)
        
        rows.append((
            schedule_date_ist,
            time_retrieved,
            block_index + 1,
            period_end_ist,
            oa_remc_oa_gna_list[block_index],
            emergency_as_list[block_index],
            shortfall_as_list[block_index],
            total_net_schd_amount_list[block_index],
            station_sch_amount_list[block_index],
            created_on_IST,
            revision_no,
            full_schd_revision_no,
            schedule_published_time_ist
        ))
    return rows

def flatten_block_jsonb(time_retrieved, schedule_data: dict):
    """
    Convert one tata_schedule jsonb row's FullschdList into 96-rows-per-item.

    Return tuple matches tata_schedule_block_structured column order:
    (schedule_date_ist, time_retrieved, period_end_ist, time_block,
     approval_no, block_id,
     link_name, as_type_name, energy_schedule_type_name, energy_schedule_subtype_name,
     px_exchange_type_name, px_transaction_type_name,
     buyer_acronym, seller_acronym, trader_acronym,
     buyer_parent_state_util_acronym, buyer_parent_discom_util_acronym,
     buyer_unit_acronym, seller_unit_acronym, is_unit_wise_buyer, is_unit_wise_seller,
     data_integration_timing_type_name,
     schd_amount, poc_drawal_loss, state_drawal_loss, poc_injection_loss, state_injection_loss,
     discom_or_emb_in_state_drw_loss, discom_or_emb_in_state_inj_loss,
     total_drw_boundary_schd_amount, total_inj_boundary_schd_amount, total_reg_boundary_schd_amount,
     full_schd_revision_no, schedule_published_time_ist)
    """
    response_body = schedule_data["data"]["ResponseBody"]
    group = response_body["GroupWiseDataList"][0]

    schedule_date_ist = datetime.datetime.strptime(response_body["Date"], "%d-%m-%Y").date()
    full_schd_revision_no = response_body["FullSchdRevisionNo"]
    schedule_published_time_ist = datetime.datetime.fromisoformat(response_body["SchedulePublishedTime"])

    rows = []
    for item in group["FullschdList"]:
        # Exactly one of these is populated per FullschdList entry.
        series = next(
            (v for v in item["FullScheduleData"].values() if v is not None),
            None,
        )
        if series is None:
            continue

        approval_no = item["ApprovalNo"] or ""
        block_id = _block_id_from_approval_no(approval_no)

        schd_amount_list = series["SchdAmount"]
        poc_drawal_loss_list = series.get("POCDrawalLoss")
        state_drawal_loss_list = series.get("StateDrawalLoss")
        poc_injection_loss_list = series.get("POCInjectionLoss")
        state_injection_loss_list = series.get("StateInjectionLoss")
        discom_or_emb_in_state_drw_loss_list = series.get("DiscomOrEmbInStateDrwLoss")
        discom_or_emb_in_state_inj_loss_list = series.get("DiscomOrEmbInStateInjLoss")
        total_drw_boundary_schd_amount_list = series.get("TotalDrwBoundarySchdAmount")
        total_inj_boundary_schd_amount_list = series.get("TotalInjBoundarySchdAmount")
        total_reg_boundary_schd_amount_list = series.get("TotalRegBoundarySchdAmount")

        for block_index in range(96):
            rows.append((
                schedule_date_ist,
                time_retrieved,
                _period_end_ist(schedule_date_ist, block_index),
                block_index + 1,
                approval_no,
                block_id,
                item["LinkName"] or "",
                item["ASTypeName"],
                item["EnergyScheduleTypeName"],
                item["EnergyScheduleSubTypeName"],
                item["PXExchangeTypeName"],
                item["PXTransactionTypeName"],
                item["BuyerAcronym"] or "",
                item["SellerAcronym"] or "",
                item["TraderAcronym"] or "",
                item["BuyerParentStateUtilAcronym"] or "",
                item["BuyerParentDiscomUtilAcronym"] or "",
                item["BuyerUnitAcronym"] or "",
                item["SellerUnitAcronym"] or "",
                bool(item["IsUnitWiseBuyerFlag"]),
                bool(item["IsUnitWiseSellerFlag"]),
                item["DataIntegrationTimingTypeName"],
                _at(schd_amount_list, block_index),
                _at(poc_drawal_loss_list, block_index),
                _at(state_drawal_loss_list, block_index),
                _at(poc_injection_loss_list, block_index),
                _at(state_injection_loss_list, block_index),
                _at(discom_or_emb_in_state_drw_loss_list, block_index),
                _at(discom_or_emb_in_state_inj_loss_list, block_index),
                _at(total_drw_boundary_schd_amount_list, block_index),
                _at(total_inj_boundary_schd_amount_list, block_index),
                _at(total_reg_boundary_schd_amount_list, block_index),
                full_schd_revision_no,
                schedule_published_time_ist,
            ))
    return rows


def flatten_block_gna_jsonb(time_retrieved, schedule_data: dict):
    """
    Convert one tata_schedule jsonb row's GNAContractReqList into 96-rows-per-item.

    Return tuple matches tata_schedule_block_gna_structured column order:
    (schedule_date_ist, time_retrieved, period_end_ist, time_block,
     approval_no, block_id,
     link_name, revision_no, remc_revision_no, applicant_acronym, is_remc_transaction,
     from_date, to_date, contract_from_date, contract_to_date,
     buyer_acronym, seller_acronym, trader_acronym, buyer_unit_acronym, seller_unit_acronym,
     buyer_trader_acronym, seller_trader_acronym, is_unit_wise_buyer, is_unit_wise_seller,
     buyer_generator_type_name, seller_generator_type_name,
     buyer_generator_subtype_name, seller_generator_subtype_name,
     buyer_parent_state_util_acronym, buyer_parent_discom_util_acronym,
     seller_parent_state_util_acronym, seller_parent_discom_util_acronym,
     contract_amount, contract_dc_amount, requisitioned_amount, restriction_amount,
     psm_reg_amount, lpsc_reg_amount,
     full_schd_revision_no, schedule_published_time_ist)
    """
    response_body = schedule_data["data"]["ResponseBody"]
    group = response_body["GroupWiseDataList"][0]

    schedule_date_ist = datetime.datetime.strptime(response_body["Date"], "%d-%m-%Y").date()
    full_schd_revision_no = response_body["FullSchdRevisionNo"]
    schedule_published_time_ist = datetime.datetime.fromisoformat(response_body["SchedulePublishedTime"])

    def parse_date(s):
        return datetime.datetime.strptime(s, "%d-%m-%Y").date()

    rows = []
    for item in group["GNAContractReqList"]:
        approval_no = item["ApprovalNo"] or ""
        block_id = _block_id_from_approval_no(approval_no)

        measures = item["GNAContractReqJsonData"]
        contract_amount_list = measures["ContractAmount"]
        contract_dc_amount_list = measures["ContractDCAmount"]
        requisition_amount_list = measures["RequisitionAmount"]
        restriction_amount_list = measures["RestrictionAmount"]
        psm_reg_amount_list = measures.get("PSMRegAmount")
        lpsc_reg_amount_list = measures.get("LPSCRegAmount")

        for block_index in range(96):
            rows.append((
                schedule_date_ist,
                time_retrieved,
                _period_end_ist(schedule_date_ist, block_index),
                block_index + 1,
                approval_no,
                block_id,
                item["LinkName"] or "",
                item["RevisionNo"],
                item["REMCRevisionNo"],
                item["ApplicantAcronym"] or "",
                bool(item["IsREMCTransaction"]),
                parse_date(item["FromDate"]),
                parse_date(item["ToDate"]),
                parse_date(item["ContractFromDate"]),
                parse_date(item["ContractToDate"]),
                item["BuyerAcronym"] or "",
                item["SellerAcronym"] or "",
                item["TraderAcronym"] or "",
                item["BuyerUnitAcronym"] or "",
                item["SellerUnitAcronym"] or "",
                item["BuyerTraderAcronym"] or "",
                item["SellerTraderAcronym"] or "",
                bool(item["IsUnitWiseBuyerFlag"]),
                bool(item["IsUnitWiseSellerFlag"]),
                item["BuyerGeneratorTypeName"] or "NA",
                item["SellerGeneratorTypeName"] or "NA",
                item["BuyerGeneratorSubTypeName"] or "NA",
                item["SellerGeneratorSubTypeName"] or "NA",
                item["BuyerParentStateUtilAcronym"] or "",
                item["BuyerParentDiscomUtilAcronym"] or "",
                item["SellerParentStateUtilAcronym"] or "",
                item["SellerParentDiscomUtilAcronym"] or "",
                _at(contract_amount_list, block_index),
                _at(contract_dc_amount_list, block_index),
                _at(requisition_amount_list, block_index),
                _at(restriction_amount_list, block_index),
                _at(psm_reg_amount_list, block_index),
                _at(lpsc_reg_amount_list, block_index),
                full_schd_revision_no,
                schedule_published_time_ist,
            ))
    return rows
