import datetime

def flatten_jsonb(time_retrieved, schedule_data: dict):

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
    revision_no =group["REMCDeclarationList"][0]["RevisionNo"]

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

        period_end_time = datetime.time(
            hour=(block_index + 1) // 4 if (block_index + 1) < 96 else 0,
            minute=((block_index + 1) % 4) * 15
        )
        if period_end_time.hour == 0 and period_end_time.minute == 0:
            period_end_ist = datetime.datetime.combine(schedule_date_ist + datetime.timedelta(days=1), period_end_time)
        else:
            period_end_ist = datetime.datetime.combine(schedule_date_ist, period_end_time)
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